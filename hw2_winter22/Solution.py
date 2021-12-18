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

def _str(x) -> str:
    if x is None:
        return "NULL"

    if isinstance(x, str):
        return x

    return str(x)

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
    q = "INSERT INTO Teams (teamId) VALUES (" + _str(teamID) + ");"
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
    matchId = match.getMatchID()
    competition = match.getCompetition()
    homeTeam = match.getHomeTeamID()
    awayTeam = match.getAwayTeamID()

    q = "INSERT INTO Matches (matchId ,competition, homeTeamId, awayTeamId) VALUES ("
    q += _str(matchId) + " , '" + _str(competition) + "' , " + _str(homeTeam) + " , " + _str(awayTeam) + " );"

    return sendQuery(q).Status


def getMatchProfile(matchID: int) -> Match:
    q = "SELECT * FROM Matches WHERE matchId =" + _str(matchID) + ";"
    res = sendQuery(q)

    if res.Status != ReturnValue.OK or res.RowsAffected == 0:
        return Match.badMatch()

    return _sqlToMatch(res.Set)


def deleteMatch(match: Match) -> ReturnValue:
    q = "DELETE FROM Matches WHERE  matchId = " + _str(match.getMatchID()) + ";"

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
    playerId = player.getPlayerID()
    teamId = player.getTeamID()
    age = player.getAge()
    height = player.getHeight()
    foot = player.getFoot()

    q = "INSERT INTO players (playerId, teamId, age, height, foot) VALUES ("
    q += _str(playerId) + ", "
    q += _str(teamId) + ", "
    q += _str(age) + ", "
    q += _str(height) + ", "
    q += "'" + _str(foot) + "');"
    return sendQuery(q).Status


def getPlayerProfile(playerID: int) -> Player:
    q = "SELECT * FROM players WHERE playerId =" + _str(playerID) + ";"
    res = sendQuery(q)

    if res.Status != ReturnValue.OK or res.RowsAffected == 0:
        return Player.badPlayer()

    return _sqlToPlayer(res.Set)


def deletePlayer(player: Player) -> ReturnValue:
    q = "DELETE FROM players WHERE  playerId = " + _str(player.getPlayerID()) + ";"

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
    stadiumId = stadium.getStadiumID()
    cap = stadium.getCapacity()
    belong = stadium.getBelongsTo()

    q = "INSERT INTO stadiums (stadiumId, capacity, teamId) VALUES ("
    q += _str(stadiumId)
    q += ", " + _str(cap)
    q += ", " + _str(belong)
    q += ")"

    return sendQuery(q).Status


def getStadiumProfile(stadiumID: int) -> Stadium:
    q = "SELECT * FROM stadiums WHERE stadiumId =" + _str(stadiumID) + ";"
    res = sendQuery(q)

    if res.Status != ReturnValue.OK or res.RowsAffected == 0:
        return Stadium.badStadium()

    return _sqlToStadium(res.Set)


def deleteStadium(stadium: Stadium) -> ReturnValue:
    q = "DELETE FROM stadiums WHERE  stadiumId = " + _str(stadium.getStadiumID()) + ";"
    res = sendQuery(q)
    if res.Status == ReturnValue.OK and res.RowsAffected == 0:
        return ReturnValue.NOT_EXISTS

    return res.Status
# endregion

# region Basic API
def playerScoredInMatch(match: Match, player: Player, amount: int) -> ReturnValue:
    q = "INSERT INTO Scores (playerId, matchId, amount) VALUES ("
    q += _str(player.getPlayerID()) + ", "
    q += _str(match.getMatchID()) + ", "
    q += _str(amount) + ");"
    return sendQuery(q).Status


def playerDidntScoreInMatch(match: Match, player: Player) -> ReturnValue:
    q = "DELETE FROM Scores WHERE  matchId = " + _str(match.getMatchID()) + " AND playerId = " + _str(player.getPlayerID()) + ";"

    res = sendQuery(q)
    if res.Status == ReturnValue.OK and res.RowsAffected == 0:
        return ReturnValue.NOT_EXISTS

    return res.Status


def matchInStadium(match: Match, stadium: Stadium, attendance: int) -> ReturnValue:
    q = "INSERT INTO MatchInStadium (matchId, stadiumId, attendance) VALUES ("
    q += _str(match.getMatchID())
    q += ", " + _str(stadium.getStadiumID())
    q += ", " + _str(attendance) + ");"
    return sendQuery(q).Status


def matchNotInStadium(match: Match, stadium: Stadium) -> ReturnValue:
    q = "DELETE FROM MatchInStadium WHERE  matchId = " + _str(match.getMatchID()) + " AND stadiumId = " + _str(stadium.getStadiumID()) + ";"

    res = sendQuery(q)
    if res.Status == ReturnValue.OK and res.RowsAffected == 0:
        return ReturnValue.NOT_EXISTS

    return res.Status


def averageAttendanceInStadium(stadiumID: int) -> float:
    q = "SELECT AVG(attendance) FROM MatchInStadium WHERE stadiumId = " + _str(stadiumID)

    res = sendQuery(q)
    if res.Status != ReturnValue.OK:
        return -1

    if res.RowsAffected == 0:
        return 0

    row = res.Set.rows[0]
    return 0 if row[0] is None else row[0]


def stadiumTotalGoals(stadiumID: int) -> int:
    # sum(amount) on [(matchInStadium where stadiumId == _str(stadiumId)) join by matchId kind=leftOuter (scored)]
    q = "SELECT SUM(amount)"
    q += " FROM matchInStadium"
    q += " LEFT JOIN scores"
    q += " ON matchInStadium.matchId = scores.matchId AND matchInStadium.stadiumId = " + _str(stadiumID)

    res = sendQuery(q)
    if res.Status != ReturnValue.OK:
        return -1

    if res.RowsAffected == 0:
        return 0

    row = res.Set.rows[0]
    return 0 if row[0] is None else row[0]


def playerIsWinner(playerID: int, matchID: int) -> bool:
    q = "SELECT amount FROM Scores WHERE playerId = " + _str(playerID)
    q += " AND matchID = " + _str(matchID)
    q += " UNION SELECT SUM(amount) FROM Scores WHERE matchID = " + _str(matchID)
    res = Connector.DBConnector().execute(query=q)

    rows = res[1].rows
    playerRow = rows[0]
    totalRow = rows[1]
    playerAmount = playerRow[0]
    totalAmount = totalRow[0]
    return 2 * playerAmount >= totalAmount


def getAllTallActiveTeamsQuery():
    activeTeamsQ = ""  # TODO
    tallTeamsQ = ""  # TODO
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
    reachTeams = " "  # TODO
    q = activeTallTeamsQ + " INTERSECT " + reachTeams + " ORDER BY teamId ASC LIMIT 5"

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
