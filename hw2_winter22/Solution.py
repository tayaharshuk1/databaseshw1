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


def _errorHandling(e) -> ReturnValue:
    if isinstance(e, DatabaseException.NOT_NULL_VIOLATION) or \
            isinstance(e, DatabaseException.CHECK_VIOLATION):
        return ReturnValue.BAD_PARAMS

    if isinstance(e, DatabaseException.UNIQUE_VIOLATION):
        return ReturnValue.ALREADY_EXISTS

    if isinstance(e, DatabaseException.FOREIGN_KEY_VIOLATION):
        return ReturnValue.BAD_PARAMS

    if e.pgcode == '22001':                 # Special treatment to a case of string too large
        return ReturnValue.BAD_PARAMS

    return ReturnValue.ERROR


def sendQuery(query) -> collections.namedtuple("QueryResult", ["Status", "RowsAffected","Set"]):
    dbConnector = Connector.DBConnector()
    retValue = ReturnValue.OK
    res = None
    try:
        res = dbConnector.execute(query=query)
    except BaseException as e:
        retValue = _errorHandling(e)
    finally:
        dbConnector.close()

    queryResult = collections.namedtuple("QueryResult", ["Status","RowsAffected", "Set"])
    return queryResult(retValue, None if res is None else res[0], None if res is None else res[1])


def _createTable(name, colNames, colTypes, extraProperties, foreignKey = None, checks=None, extraStatements = None):
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

# endregion

# region table definitions
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
# endregion

# region Init

def defineViews():
    view_ActiveTallTeams = {
        "name": "",
        "query": "ActiveTallTeams",  # TODO
        "materialized": False
    }
    Views.append(view_ActiveTallTeams)


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
        pass  # TODO : Jonathan


def clearTables():
    for table in Tables:
        q = "DELETE FROM " + table["name"]


def dropTables():
    for table in reversed(Tables):
        q = "DROP TABLE " + table["name"]
        sendQuery(q)

# endregion

# region Team

def addTeam(teamID: int) -> ReturnValue:
    q = sql.SQL("INSERT INTO Teams (teamId) VALUES ({teamID});").format(teamID=sql.Literal(teamID))
    return sendQuery(q).Status

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

    return sendQuery(q).Status


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
    return sendQuery(q).Status


def getPlayerProfile(playerID: int) -> Player:
    q = sql.SQL("SELECT * FROM players WHERE playerId ={playerID};").format(playerID=sql.Literal(playerID))
    res = sendQuery(q)

    if res.Status != ReturnValue.OK or res.RowsAffected == 0:
        return Player.badPlayer()

    return _sqlToPlayer(res.Set)


def deletePlayer(player: Player) -> ReturnValue:
    q = sql.SQL("DELETE FROM players WHERE  playerId = {playerID};").format(playerId=player.getPlayerID())

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

    return sendQuery(q).Status


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
    q = (sql.SQL("DELETE FROM Scores WHERE  matchId = {matchID} AND playerId = {playerId};")
         .format(matchId = sql.Literal(match.getMatchID()), playerId = sql.Literal(player.getPlayerID())))

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
    q = sql.SQL("SELECT AVG(attendance) FROM MatchInStadium WHERE stadiumId = {x}").format(x=sql.Literal(stadiumID))

    res = sendQuery(q)
    if res.Status != ReturnValue.OK:
        return -1

    if res.RowsAffected == 0:
        return 0

    row = res.Set.rows[0]
    return 0 if row[0] is None else row[0]


def stadiumTotalGoals(stadiumID: int) -> int:
    q = (sql.SQL("SELECT SUM(amount) FROM matchInStadium LEFT JOIN scores ON matchInStadium.matchId = scores.matchId AND matchInStadium.stadiumId = {x}")
         .format(x=sql.Literal(stadiumID)))

    res = sendQuery(q)
    if res.Status != ReturnValue.OK:
        return -1

    if res.RowsAffected == 0:
        return 0

    row = res.Set.rows[0]
    return 0 if row[0] is None else row[0]


def playerIsWinner(playerID: int, matchID: int) -> bool:
    q = (sql.SQL("SELECT COALESCE(amount, 0) FROM Scores WHERE playerId = {playerID} AND matchID = {matchID}"
                 " UNION SELECT SUM(amount) FROM Scores WHERE matchID = {matchID}")
         .format(playerID=sql.Literal(playerID), matchID=sql.Literal(matchID)))

    # TODO: View that project scores on Player
    res = sendQuery(q)

    playerRow = res.Set.rows[0]
    totalRow = res.Set.rows[1]
    playerAmount = playerRow[0]
    totalAmount = totalRow[0]
    return 2 * playerAmount >= totalAmount


def getAllTallActiveTeamsQuery():
    activeTeamsQ = ""   #TODO: from the views?
    tallTeamsQ = ""  # TODO : group by?
    q = activeTeamsQ + " INTERSECT " + tallTeamsQ
    return q


def getActiveTallTeams() -> List[int]:
    q = getAllTallActiveTeamsQuery() + " ORDER BY teamId DESC LIMIT 5"

    res = Connector.DBConnector().execute(query=q)
    teams = []
    for row in res[1]:
        teams.append(row[0])
        # TODO: check of int

    return teams


def getActiveTallRichTeams() -> List[int]:
    activeTallTeamsQ = getAllTallActiveTeamsQuery()
    richTeams = "SELECT teamID FROM Stadiums WHERE capacity>" + _str(55000)   #TODO :check
    q = activeTallTeamsQ + " INTERSECT " + richTeams + " ORDER BY teamId ASC LIMIT 5"

    res = Connector.DBConnector().execute(query=q)
    teams = []
    for row in res[1]:
        teams.append(row[0])
        # TODO: check of int

    return teams


def popularTeams() -> List[int]:
    pass

# endregion

# region Advanced API
def getMostAttractiveStadiums() -> List[int]:
    pass


def mostGoalsForTeam(teamID: int) -> List[int]:
    pass


def getClosePlayers(playerID: int) -> List[int]:
    pass
# endregion
