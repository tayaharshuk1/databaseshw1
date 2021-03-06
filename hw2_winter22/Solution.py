import collections
from typing import List

from pycparser.c_ast import Return

import Utility.DBConnector as Connector
from Utility.ReturnValue import ReturnValue
from Utility.Exceptions import DatabaseException
from Business.Match import Match
from Business.Player import Player
from Business.Stadium import Stadium
from psycopg2 import sql

# region Utils
Tables = []
Views = []


def _errorHandling(e, isCrud: bool = False) -> ReturnValue:
    if isinstance(e, DatabaseException.NOT_NULL_VIOLATION) or \
            isinstance(e, DatabaseException.CHECK_VIOLATION):
        return ReturnValue.BAD_PARAMS

    if isinstance(e, DatabaseException.UNIQUE_VIOLATION):
        return ReturnValue.ALREADY_EXISTS

    if isinstance(e, DatabaseException.FOREIGN_KEY_VIOLATION) and isCrud:
        return ReturnValue.BAD_PARAMS

    if isinstance(e, DatabaseException.FOREIGN_KEY_VIOLATION):
        return ReturnValue.NOT_EXISTS

    if e.pgcode == '22001':                 # Special treatment to a case of string too large
        return ReturnValue.BAD_PARAMS

    return ReturnValue.ERROR


def sendQuery(query, isCrud: bool = False) -> collections.namedtuple("QueryResult", ["Status", "RowsAffected","Set"]):
    dbConnector = Connector.DBConnector()
    retValue = ReturnValue.OK
    res = None
    try:
        res = dbConnector.execute(query=query)
    except BaseException as e:
        retValue = _errorHandling(e, isCrud)
    finally:
        dbConnector.close()

    queryResult = collections.namedtuple("QueryResult", ["Status","RowsAffected", "Set"])
    return queryResult(retValue, None if res is None else res[0], None if res is None else res[1])


def _createTable(name, colNames, colTypes, extraProperties, foreignKey=None, checks=None, extraStatements=None):
    """
    :param name: The Table name
    :param colNames: a list of column names
    :param colTypes: a list of column types
    :param extraProperties: Extra properties per parameter. e.g: UNIQUE, PRIMARY KEY, NOT NULL, etc.
    :param foreignKey: a list of tuple in the format of (col names, reference, toDelete).
        colName is a col which is a foreign key.
        The reference is the reference string in the format of Table(col).
        toDelete is a boolean list that state whether a foreign key need to enforce delete from reference table
    :param checks: To add a check to cols. (e.g., teamId > 0 )
    :param extraStatements: Sometimes, we need more generic statements. (e.g., explicit primary keys, checks, etc.)
    :return: a dictionary with the table metadata for the table generator
    """
    if foreignKey is None:
        foreignKey = []
    if extraStatements is None:
        extraStatements = []
    if checks is None:
        checks = []

    assert len(colNames) == len(colTypes)
    assert len(colNames) == len(extraProperties)

    return {
        "name": name,
        "colNames": colNames,
        "colTypes": colTypes,
        "extraProperties": extraProperties,
        "foreignKey": foreignKey,
        "checks": checks,
        "extraStatements": extraStatements
    }


def _createView(name, query, toMaterialize):
    return {
        "name": name,
        "query": query,
        "toMaterialize": toMaterialize
    }

# endregion

# region table & view definitions
def defineTables():
    table_Teams = _createTable(name="Teams",
                               colNames=["teamId"],
                               colTypes=["int"],
                               checks=["teamId > 0"],
                               extraProperties=["PRIMARY KEY"])

    table_Players = _createTable(name="Players",
                                 colNames=["playerId", "teamId", "age", "height", "foot"],
                                 colTypes=["int", "int", "int", "int", "varchar(8)"],
                                 extraProperties=["PRIMARY KEY", "NOT NULL", "NOT NULL", "NOT NULL", "NOT NULL"],
                                 foreignKey=[("teamId", "Teams(teamId)", True)],
                                 checks=["playerId > 0", "age > 0", "height > 0", "foot = 'Right' OR foot = 'Left'"])

    table_Matches = _createTable(name="Matches",
                                 colNames=["matchId", "competition", "homeTeamId", "awayTeamId"],
                                 colTypes=["int", "varchar(16)", "int", "int"],
                                 extraProperties=["PRIMARY KEY", "NOT NULL", "NOT NULL", "NOT NULL"],
                                 checks=["matchId > 0", "homeTeamId != awayTeamId", "competition = 'International' OR competition = 'Domestic'"])

    table_Stadiums = _createTable(name="Stadiums",
                                  colNames=["stadiumId", "capacity", "teamId"],
                                  colTypes=["int", "int", "int"],
                                  extraProperties=["PRIMARY KEY", "NOT NULL", "UNIQUE"],
                                  foreignKey=[("teamId", "Teams(teamId)", True)],
                                  checks=["stadiumId > 0", "capacity > 0"])

    table_Scores = _createTable(name="Scores",
                                colNames=["playerId", "matchId", "amount"],
                                colTypes=["int", "int", "int"],
                                extraProperties=["NOT NULL", "NOT NULL", "NOT NULL"],
                                foreignKey=[("playerId", "Players(playerId)", True), ("matchId", "Matches(matchId)", True)],
                                checks=["amount > 0"],
                                extraStatements=[", CONSTRAINT match_player PRIMARY KEY (playerId, matchId)"])

    table_MatchInStadium = _createTable(name="MatchInStadium",
                                        colNames=["matchId", "stadiumId", "attendance"],
                                        colTypes=["int", "int", "int"],
                                        extraProperties=["PRIMARY KEY", "NOT NULL", "NOT NULL"],
                                        foreignKey=[("matchId", "Matches(matchId)", True)],
                                        checks=["attendance > 0"])

    Tables.append(table_Teams)
    Tables.append(table_Players)
    Tables.append(table_Matches)
    Tables.append(table_Stadiums)
    Tables.append(table_Scores)
    Tables.append(table_MatchInStadium)


def defineViews():
    view_personalStats = _createView(name="personalStats",
                                     query="SELECT Players.playerid, matchId, COALESCE(amount, 0) AS amount FROM Players LEFT JOIN scores ON Players.playerId = scores.playerId",
                                     toMaterialize=False)

    view_goalsPerMatch = _createView(name="goalsPerMatch",
                                     query="SELECT SUM(amount) AS goals, matchId FROM Scores GROUP BY matchId",
                                     toMaterialize=False)

    view_goalsPerPlayer = _createView(name="goalsPerPlayer",
                                      query="SELECT Players.playerId AS playerId, Players.teamId AS teamId, COALESCE(SUM(amount), 0) AS amount FROM players "
                                            "LEFT JOIN Scores ON Players.playerId = Scores.playerId GROUP BY Players.playerId",
                                      toMaterialize=False)

    view_ActiveTeams = _createView(name="activeTeams",
                                   query="SELECT DISTINCT homeTeamId AS teamId FROM Matches UNION SELECT DISTINCT awayTeamId FROM Matches",
                                   toMaterialize=False)

    view_TallTeams = _createView(name="tallTeams",
                                 query="SELECT teamId FROM (SELECT teamId, COUNT(*) FROM Players WHERE height > 190 GROUP BY teamId) countTable WHERE count >= 2",
                                 toMaterialize=False)

    view_ActiveTallTeams = _createView(name="activeTallTeams",
                                       query="SELECT * FROM tallTeams INTERSECT SELECT * FROM activeTeams",
                                       toMaterialize=False)

    view_minAttendancePerTeam = _createView(name="minAttendancePerTeam",
                                            query="SELECT homeTeamId AS teamId, MIN(COALESCE(attendance, 0)) AS attendance "
                                                  "FROM Matches LEFT JOIN MatchInStadium ON Matches.matchId = MatchInStadium.matchId "
                                                  "GROUP BY homeTeamId",
                                            toMaterialize=False)

    # In stadiums that had matches in them
    view_goalsPerStadium = _createView(name="goalsPerStadium",
                                            query="SELECT stadiumId, SUM(COALESCE(goals, 0)) AS goals "
                                                  "FROM matchInStadium LEFT JOIN goalsPerMatch ON matchInStadium.matchId = goalsPerMatch.matchId "
                                                  "GROUP BY stadiumId",
                                            toMaterialize=False)

    view_friends = _createView(name="friends",
                               query="SELECT P1.PlayerId AS pid1, P2.PlayerId AS pid2 FROM Scores P1, Scores P2 WHERE P1.matchId = P2.matchId",
                               toMaterialize=False)



    Views.append(view_personalStats)
    Views.append(view_goalsPerMatch)
    Views.append(view_goalsPerPlayer)
    Views.append(view_ActiveTeams)
    Views.append(view_TallTeams)
    Views.append(view_ActiveTallTeams)
    Views.append(view_minAttendancePerTeam)
    Views.append(view_goalsPerStadium)
    Views.append(view_friends)
# endregion

# region Init
def createTables():
    defineTables()
    defineViews()

    # TODO: delete before submission
    dropTables()

    # Table creator generator
    for table in Tables:
        q = "CREATE TABLE " + table["name"] + " ("

        # add cols
        for col_index in range(len(table["colNames"])):
            q += table["colNames"][col_index] + " " + table["colTypes"][col_index]
            q += " " + table["extraProperties"][col_index]
            if col_index < len(table["colNames"]) - 1:
                q += ", "

        # add foreign keys if exists
        for key, ref, onDelete in table["foreignKey"]:
            q += ", FOREIGN KEY ("+key+") REFERENCES "+ref
            if onDelete:
                q += " ON DELETE CASCADE"

        # add checks
        for check in table["checks"]:
            q += ", CHECK(" + check + ")"

        # add special primary keys if exists
        for extraStatements in table["extraStatements"]:
            q += extraStatements

        q += ");"

        sendQuery(q)

    for view in Views:
        q = "CREATE "
        if view["toMaterialize"]:
            q += "MATERIALIZED "
        q += "VIEW " + view["name"] + " AS " + view["query"] + ";"
        sendQuery(q)


def clearTables():
    for table in reversed(Tables):
        q = "DELETE FROM " + table["name"]
        sendQuery(q)


def dropTables():
    for view in reversed(Views):
        q = "DROP "
        if view["toMaterialize"]:
            q += "MATERIALIZED "
        q += "VIEW " + view["name"]
        sendQuery(q)

    for table in reversed(Tables):
        q = "DROP TABLE " + table["name"]
        sendQuery(q)


# endregion

# region Team

def addTeam(teamID: int) -> ReturnValue:
    q = sql.SQL("INSERT INTO Teams (teamId) VALUES ({teamID});").format(teamID=sql.Literal(teamID))
    return sendQuery(q, True).Status

# endregion

# region Match
def _sqlToMatch(res: Connector.ResultSet) -> Match:
    row = res.rows[0]
    matchId = row[0]
    competition = row[1]
    homeTeamID = row[2]
    awayTeamID = row[3]

    return Match(matchId, competition, homeTeamID, awayTeamID)


def addMatch(match: Match) -> ReturnValue:
    q = (sql.SQL("INSERT INTO Matches (matchId ,competition, homeTeamId, awayTeamId) VALUES ({matchId}, {competition}, {homeTeamId}, {awayTeamId});")
         .format(matchId=sql.Literal(match.getMatchID()),
                 competition=sql.Literal(match.getCompetition()),
                 homeTeamId=sql.Literal(match.getHomeTeamID()),
                 awayTeamId=sql.Literal(match.getAwayTeamID())
                 ))

    return sendQuery(q, True).Status


def getMatchProfile(matchID: int) -> Match:
    q = sql.SQL("SELECT * FROM Matches WHERE matchId ={matchID};").format(matchID=sql.Literal(matchID))
    res = sendQuery(q)

    if res.Status != ReturnValue.OK or res.RowsAffected == 0:
        return Match.badMatch()

    return _sqlToMatch(res.Set)


def deleteMatch(match: Match) -> ReturnValue:
    q = sql.SQL("DELETE FROM Matches WHERE  matchId = {matchID};").format(matchID=sql.Literal(match.getMatchID()))

    res = sendQuery(q)
    if res.Status == ReturnValue.OK and res.RowsAffected == 0:
        return ReturnValue.NOT_EXISTS

    return res.Status

# endregion

# region Player
def _sqlToPlayer(res: Connector.ResultSet) -> Player:
    row = res.rows[0]
    return Player(playerID=row[0],
                  teamID=row[1],
                  age=row[2],
                  height=row[3],
                  foot=row[4])


def addPlayer(player: Player) -> ReturnValue:
    q = (sql.SQL("INSERT INTO players (playerId, teamId, age, height, foot) VALUES ({playerId}, {teamId}, {age}, {height}, {foot});")
         .format(playerId=sql.Literal(player.getPlayerID()),
                 teamId=sql.Literal(player.getTeamID()),
                 age=sql.Literal(player.getAge()),
                 height=sql.Literal(player.getHeight()),
                 foot=sql.Literal(player.getFoot())
                 ))
    return sendQuery(q, True).Status


def getPlayerProfile(playerID: int) -> Player:
    q = sql.SQL("SELECT * FROM players WHERE playerId ={playerID};").format(playerID=sql.Literal(playerID))
    res = sendQuery(q)

    if res.Status != ReturnValue.OK or res.RowsAffected == 0:
        return Player.badPlayer()

    return _sqlToPlayer(res.Set)


def deletePlayer(player: Player) -> ReturnValue:
    q = sql.SQL("DELETE FROM players WHERE  playerId = {playerId};").format(playerId=sql.Literal(player.getPlayerID()))

    res = sendQuery(q)
    if res.Status == ReturnValue.OK and res.RowsAffected == 0:
        return ReturnValue.NOT_EXISTS

    return res.Status
# endregion

# region Stadium
def _sqlToStadium(res: Connector.ResultSet) -> Stadium:
    row = res.rows[0]
    return Stadium(stadiumID=row[0],
                   capacity=row[1],
                   belongsTo=row[2])


def addStadium(stadium: Stadium) -> ReturnValue:
    # TODO: check return ALREADY_EXISTS if a Stadium with the same ID already exists or the team already owns a stadium

    q = (sql.SQL("INSERT INTO stadiums (stadiumId, capacity, teamId) VALUES ({stadiumId}, {cap}, {belong});")
         .format(stadiumId=sql.Literal(stadium.getStadiumID()),
                 cap=sql.Literal(stadium.getCapacity()),
                 belong=sql.Literal(stadium.getBelongsTo())))

    return sendQuery(q, True).Status


def getStadiumProfile(stadiumID: int) -> Stadium:
    q = sql.SQL("SELECT * FROM stadiums WHERE stadiumId = {stadiumID};").format(stadiumID=sql.Literal(stadiumID))
    res = sendQuery(q)

    if res.Status != ReturnValue.OK or res.RowsAffected == 0:
        return Stadium.badStadium()

    return _sqlToStadium(res.Set)


def deleteStadium(stadium: Stadium) -> ReturnValue:
    q = sql.SQL("DELETE FROM stadiums WHERE stadiumId = {stadiumID};").format(stadiumID=sql.Literal(stadium.getStadiumID()))
    res = sendQuery(q)
    if res.Status == ReturnValue.OK and res.RowsAffected == 0:
        return ReturnValue.NOT_EXISTS

    return res.Status
# endregion

# region Basic API
def playerScoredInMatch(match: Match, player: Player, amount: int) -> ReturnValue:
    q = (sql.SQL("INSERT INTO Scores (playerId, matchId, amount) VALUES ({playerId},{matchId},{amount});")
         .format(playerId=sql.Literal(player.getPlayerID()),
                 matchId=sql.Literal(match.getMatchID()),
                 amount=sql.Literal(amount)))

    return sendQuery(q).Status


def playerDidntScoreInMatch(match: Match, player: Player) -> ReturnValue:
    q = (sql.SQL("DELETE FROM Scores WHERE  matchId = {matchId} AND playerId = {playerId};")
         .format(matchId=sql.Literal(match.getMatchID()), playerId=sql.Literal(player.getPlayerID())))

    res = sendQuery(q)
    if res.Status == ReturnValue.OK and res.RowsAffected == 0:
        return ReturnValue.NOT_EXISTS

    return res.Status


def matchInStadium(match: Match, stadium: Stadium, attendance: int) -> ReturnValue:
    q = (sql.SQL("INSERT INTO MatchInStadium (matchId, stadiumId, attendance) VALUES ({matchId}, {stadiumId}, {attendance});")
         .format(matchId=sql.Literal(match.getMatchID()),
                 stadiumId=sql.Literal(stadium.getStadiumID()),
                 attendance=sql.Literal(attendance)))
    return sendQuery(q).Status


def matchNotInStadium(match: Match, stadium: Stadium) -> ReturnValue:
    q = (sql.SQL("DELETE FROM MatchInStadium WHERE matchId = {matchId} AND stadiumId = {stadiumId};")
         .format(matchId=sql.Literal(match.getMatchID()),
                 stadiumId=sql.Literal(stadium.getStadiumID())))

    res = sendQuery(q)
    if res.Status == ReturnValue.OK and res.RowsAffected == 0:
        return ReturnValue.NOT_EXISTS

    return res.Status


def averageAttendanceInStadium(stadiumID: int) -> float:
    q = sql.SQL("SELECT COALESCE(AVG(attendance), 0) FROM MatchInStadium WHERE stadiumId = {x}").format(x=sql.Literal(stadiumID))

    res = sendQuery(q)
    if res.Status != ReturnValue.OK:
        return -1

    if res.RowsAffected == 0:
        return 0

    row = res.Set.rows[0]
    return row[0]


def stadiumTotalGoals(stadiumID: int) -> int:
    q = (sql.SQL("SELECT COALESCE(SUM(amount), 0) FROM matchInStadium LEFT JOIN scores ON matchInStadium.matchId = scores.matchId AND matchInStadium.stadiumId = {x}")
         .format(x=sql.Literal(stadiumID)))

    res = sendQuery(q)
    if res.Status != ReturnValue.OK:
        return -1

    if res.RowsAffected == 0:
        return 0

    row = res.Set.rows[0]
    return row[0]


def playerIsWinner(playerID: int, matchID: int) -> bool:
    q = (sql.SQL("SELECT amount FROM personalStats WHERE playerId = {playerID} AND matchID = {matchID}"
                 " UNION ALL SELECT goals AS amount FROM goalsPerMatch WHERE matchID = {matchID}")
         .format(playerID=sql.Literal(playerID), matchID=sql.Literal(matchID)))

    res = sendQuery(q)

    if res.Status != ReturnValue.OK or res.RowsAffected < 2:
        return False

    playerAmount = res.Set.rows[0][0]
    totalAmount = res.Set.rows[1][0]
    return 2 * playerAmount >= totalAmount


def getActiveTallTeams() -> List[int]:
    q = "SELECT * FROM activeTallTeams ORDER BY teamId DESC LIMIT 5"
    teams = []

    res = sendQuery(q)

    if res.Status != ReturnValue.OK:
        return teams

    for row in res.Set.rows:
        teams.append(row[0])

    return teams


def getActiveTallRichTeams() -> List[int]:
    q = "SELECT teamId FROM activeTallTeams INTERSECT SELECT teamId FROM Stadiums WHERE capacity > 55000 ORDER BY teamId ASC LIMIT 5"
    teams = []

    res = sendQuery(q)

    if res.Status != ReturnValue.OK:
        return teams

    for row in res.Set.rows:
        teams.append(row[0])

    return teams


def popularTeams() -> List[int]:
    teams = []
    q = ("SELECT teamId FROM "
         "(SELECT Teams.teamId AS teamId, attendance FROM Teams LEFT JOIN minAttendancePerTeam ON Teams.teamId = minAttendancePerTeam.teamId) t"
         " WHERE attendance > 40000 OR attendance IS NULL ORDER BY teamId DESC LIMIT 10")
    res = sendQuery(q)

    if res.Status != ReturnValue.OK:
        return teams

    for row in res.Set.rows:
        teams.append(row[0])

    return teams
# endregion

# region Advanced API
def getMostAttractiveStadiums() -> List[int]:
    stadiums = []
    q = ("SELECT Stadiums.stadiumId AS stadiumId, COALESCE(goals, 0) AS goals FROM Stadiums "
         "LEFT JOIN goalsPerStadium ON Stadiums.stadiumId = goalsPerStadium.stadiumId "
         "ORDER BY goals DESC, stadiumId ASC;")
    res = sendQuery(q)

    if res.Status != ReturnValue.OK:
        return stadiums

    for row in res.Set.rows:
        stadiums.append(row[0])

    return stadiums


def mostGoalsForTeam(teamID: int) -> List[int]:
    players = []
    q = (sql.SQL("SELECT playerId FROM goalsPerPlayer WHERE teamId = {teamId} ORDER BY amount DESC, playerId DESC LIMIT 5")
         .format(teamId=sql.Literal(teamID)))
    res = sendQuery(q)

    if res.Status != ReturnValue.OK:
        return players

    for row in res.Set.rows:
        players.append(row[0])

    return players


def getClosePlayers(playerID: int) -> List[int]:
    players = []
    str_nested1 = "SELECT pid1, COUNT(pid1) AS playedTogether FROM friends WHERE pid2 = {playerId} GROUP BY pid1"
    str_nested2 = "SELECT Players.playerId AS pid, COALESCE(n1.playedTogether, 0) AS playedTogether FROM Players LEFT JOIN (" + str_nested1 + ") n1 ON Players.playerId = n1.pid1"
    str_q = ("SELECT n2.pid "
             "FROM (SELECT MAX(n2.playedTogether) AS max FROM (" + str_nested2 + ") n2) n3, (" + str_nested2 + ") n2 "
             "WHERE n2.pid <> {playerId} AND n2.playedTogether * 2 >= n3.max ORDER BY n2.pid ASC LIMIT 10")

    q = sql.SQL(str_q).format(playerId=sql.Literal(playerID))
    res = sendQuery(q)

    if res.Status != ReturnValue.OK:
        return players

    for row in res.Set.rows:
        players.append(row[0])

    return players
# endregion
