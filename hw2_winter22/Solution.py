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

    if isinstance(e, DatabaseException.database_ini_ERROR) or \
            isinstance(e, DatabaseException.ConnectionInvalid):
        return ReturnValue.ERROR

    return ReturnValue.OK
    # return ReturnValue.UNKNOWN_ERROR


def sendQuery(query) -> collections.namedtuple("QueryResult", ["Status", "Set"]):
    dbConnector = Connector.DBConnector()
    retValue = ReturnValue.OK
    res = None
    try:
        res = dbConnector.execute(query=query)
    except BaseException as e:
        retValue = _errorHandling(e)
    finally:
        dbConnector.close()

    queryResult = collections.namedtuple("QueryResult", ["Status", "Set"])
    return queryResult(retValue, res)


def _createTable(name, colNames, colTypes, extraProperties, foreignKey = None, references = None, explicitPrimaryKey = None):
    """
    :param name: The Table name
    :param colNames: a list of column names
    :param colTypes: a list of column types
    :param extraProperties: Extra properties per parameter. e.g: UNIQUE, PRIMARY KEY, NOT NULL, etc.
    :param foreignKey: a list of col names (each name must be contained in 'colNames'), which are a foreign keys
    :param references: a list of strings represent the references of the foreign keys. Should have a format of 'Table(relevantCol)'.
    :param explicitPrimaryKey: Sometimes, we'll want to set new col explicitly for a Primary key (mainly if the key consists multiple cols)
            Should be a tuple of ('newColName', 'col1, col2, col3')
    :return: a dictionary with the table metadata for the table generator
    """
    if foreignKey is None:
        foreignKey = []
    if references is None:
        references = []
    if explicitPrimaryKey is None:
        explicitPrimaryKey = []

    assert len(colNames) == len(colTypes)
    assert len(colNames) == len(extraProperties)
    assert len(foreignKey) == len(references)

    return {
        "name": name,
        "colNames": colNames,
        "colTypes": colTypes,
        "extraProperties": extraProperties,
        "foreignKey": foreignKey,
        "references": references,
        "explicitPrimaryKey": explicitPrimaryKey
    }

# endregion

# region Init
def defineTables():
    table_Teams = _createTable(name="Teams",
                               colNames=["teamId"],
                               colTypes=["int"],
                               extraProperties=["PRIMARY KEY"])

    table_Players = _createTable(name="Players",
                                 colNames=["playerId", "teamId", "age", "height", "preferredFoot"],
                                 colTypes=["int", "int", "int", "int", "varchar(255)"],
                                 extraProperties=["PRIMARY KEY", "NOT NULL", "NOT NULL", "NOT NULL", "NOT NULL"],
                                 foreignKey=["teamId"],
                                 references=["Teams(teamId)"])

    table_Matches = _createTable(name="Matches",
                                 colNames=["matchId", "competition", "homeTeamId", "awayTeamId"],
                                 colTypes=["int", "varchar(255)", "int", "int"],
                                 extraProperties=["PRIMARY KEY", "NOT NULL", "NOT NULL", "NOT NULL"])

    table_Stadiums = _createTable(name="Stadiums",
                                  colNames=["stadiumId", "capacity", "teamId"],
                                  colTypes=["int", "int", "int"],
                                  extraProperties=["PRIMARY KEY", "NOT NULL", "UNIQUE"],
                                  foreignKey=["teamId"],
                                  references=["Teams(teamId)"])

    table_Scores = _createTable(name="Scores",
                                colNames=["playerId", "matchId", "amount"],
                                colTypes=["int", "int", "int"],
                                extraProperties=["NOT NULL", "NOT NULL", "NOT NULL"],
                                foreignKey=["playerId", "matchId"],
                                references=["Players(playerId)", "Matches(matchId)"],
                                explicitPrimaryKey=[("match_player", "playerId, matchId")])

    table_MatchInStadium = _createTable(name="MatchInStadium",
                                        colNames=["matchId", "stadiumId", "attendance"],
                                        colTypes=["int", "int", "int"],
                                        extraProperties=["UNIQUE NOT NULL", "NOT NULL", "NOT NULL"])

    Tables.append(table_Teams)
    Tables.append(table_Players)
    Tables.append(table_Matches)
    Tables.append(table_Stadiums)
    Tables.append(table_Scores)
    Tables.append(table_MatchInStadium)


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
        for key, ref in zip(table["foreignKey"], table["references"]):
            q += ", FOREIGN KEY ("+key+") REFERENCES "+ref

        # add special primary keys if exists
        for newCol, oldCols in table["explicitPrimaryKey"]:
            q += ", CONSTRAINT " + newCol + " PRIMARY KEY (" + oldCols + ")"

        q += ")"

        sendQuery(q)

    for view in Views:
        pass  # TODO : Jonathan


def clearTables():
    for table in Tables:
        q = "DELETE FROM " + table["name"]


def dropTables():
    Tables.reverse()
    for table in Tables:
        q = "DROP TABLE " + table["name"]
        sendQuery(q)

# endregion

# region Team

def addTeam(teamID: int) -> ReturnValue:
    if teamID <= 0:
        return ReturnValue.BAD_PARAMS

    q = "INSERT INTO Teams (teamId) VALUES (" + str(teamID) + ");"
    return sendQuery(q).Status

# endregion

# region Match
def _sqlToMatch(res: Connector.ResultSet) -> Match:
    row = res[1].rows[0]
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

    if None in [matchId, competition, homeTeam, awayTeam]:
        return ReturnValue.BAD_PARAMS

    if matchId <= 0 or competition not in ["International", "Domestic"] or homeTeam == awayTeam:
        return ReturnValue.BAD_PARAMS

    q = "INSERT INTO Matches (matchId ,competition, homeTeamId, awayTeamId) VALUES ("
    q += str(matchId) + " , '" + competition + "' , " + str(homeTeam) + " , " + str(awayTeam) + " );"

    return sendQuery(q).Status  # TODO: check non-positive/non-existence teams and look for "Bad Params"


def getMatchProfile(matchID: int) -> Match:
    q = "SELECT * FROM Matches WHERE matchId =" + str(matchID) + ";"
    res = sendQuery(q)

    if res.Status != ReturnValue.OK:
        return Match.badMatch()

    return _sqlToMatch(res.Set)


def deleteMatch(match: Match) -> ReturnValue:
    q = "DELETE FROM Matches WHERE  matchId = " + str(match.getMatchID()) + ";"

    return sendQuery(q).Status

# endregion

# region Player
def _sqlToPlayer(res: Connector.ResultSet) -> Player:
    row = res[1].rows[0]
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

    if None in [playerId, teamId, age, height, foot]:
        return ReturnValue.BAD_PARAMS

    if min(playerId, teamId, age, height) <= 0 or foot not in ["Left", "Right"]:
        return ReturnValue.BAD_PARAMS

    q = "INSERT INTO players (playerId, teamId, age, height, preferredFoot) VALUES ("
    q += str(playerId) + ", "
    q += str(teamId) + ", "
    q += str(age) + ", "
    q += str(height) + ", "
    q += "'" + str(foot) + "');"
    return sendQuery(q).Status


def getPlayerProfile(playerID: int) -> Player:
    q = "SELECT * FROM players WHERE playerId =" + str(playerID) + ";"
    res = sendQuery(q)

    if res.Status != ReturnValue.OK:
        return Player.badPlayer()

    return _sqlToPlayer(res.Set)


def deletePlayer(player: Player) -> ReturnValue:
    q = "DELETE FROM players WHERE  playerId = " + str(player.getPlayerID()) + ";"

    return sendQuery(q).Status
# endregion

# region Stadium
def _sqlToStadium(res: Connector.ResultSet) -> Stadium:
    row = res[1].rows[0]
    return Stadium(stadiumID=row[0],
                   capacity=row[1],
                   belongsTo=row[2])    #TODO: check if ok with Null


def addStadium(stadium: Stadium) -> ReturnValue:
    # TODO: check return ALREADY_EXISTS if a Stadium with the same ID already exists or the team already owns a stadium
    stadiumId = stadium.getStadiumID()
    cap = stadium.getCapacity()
    belong = stadium.getBelongsTo()

    if None in [stadiumId, cap] or min(stadiumId, cap) <= 0 or (belong and belong <= 0):    # Last one is a bit tricky, it checks if 'belong' is valid only of it isn't None
        return ReturnValue.BAD_PARAMS

    q = "INSERT INTO stadiums (stadiumId, capacity"
    if belong:
        q += ", teamId"
    q += ") VALUES ("
    q += str(stadiumId)
    q += ", " + str(cap)
    if belong:
        q += ", " + str(belong)
    q += ")"

    return sendQuery(q).Status


def getStadiumProfile(stadiumID: int) -> Stadium:
    q = "SELECT * FROM stadiums WHERE stadiumId =" + str(stadiumID) + ";"
    res = sendQuery(q)

    if res.Status != ReturnValue.OK:
        return Stadium.badStadium()

    return _sqlToStadium(res.Set)


def deleteStadium(stadium: Stadium) -> ReturnValue:
    q = "DELETE FROM stadiums WHERE  stadiumId = " + str(stadium.getStadiumID()) + ";"

    return sendQuery(q).Status
# endregion

# region Basic API
def playerScoredInMatch(match: Match, player: Player, amount: int) -> ReturnValue:
    if amount <= 0:
        return ReturnValue.BAD_PARAMS

    q = "INSERT INTO ScoresScores (playerId, matchId, amount) VALUES ("
    q += str(player.getPlayerID()) + ", "
    q += str(match.getMatchID()) + ", "
    q += str(amount) + ");"
    return sendQuery(q).Status

def playerDidntScoreInMatch(match: Match, player: Player) -> ReturnValue:
    pass


def matchInStadium(match: Match, stadium: Stadium, attendance: int) -> ReturnValue:
    pass


def matchNotInStadium(match: Match, stadium: Stadium) -> ReturnValue:
    pass


def averageAttendanceInStadium(stadiumID: int) -> float:
    pass


def stadiumTotalGoals(stadiumID: int) -> int:
    # sum(amount) on [(matchInStadium where stadiumId == str(stadiumId)) join by matchId kind=leftOuter (scored)]
    pass


def playerIsWinner(playerID: int, matchID: int) -> bool:
    q = "SELECT amount FROM Scores WHERE playerId == " + str(playerID)
    q += " AND matchID == " + str(matchID)
    q += " UNION SELECT SUM(amount) FROM Scores WHERE matchID == " + str(matchID)
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
