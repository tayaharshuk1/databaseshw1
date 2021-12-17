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
    if isinstance(e, DatabaseException.UNIQUE_VIOLATION):
        return ReturnValue.ALREADY_EXISTS

    if isinstance(e, DatabaseException.FOREIGN_KEY_VIOLATION):
        return ReturnValue.BAD_PARAMS

    if isinstance(e, DatabaseException.database_ini_ERROR):
        return ReturnValue.NOT_EXISTS

    return ReturnValue.OK


def sendQuery(query) -> collections.namedtuple("QueryResult", ["Status", "Set"]):
    dbConnector = Connector.DBConnector()
    retValue = ReturnValue.OK
    res = None
    try:
        res = dbConnector.execute(query=query)
    except BaseException as e:
        retValue = _errorHandling(e)

    dbConnector.close()

    queryResult = collections.namedtuple("QueryResult", ["Status", "Set"])
    return queryResult(retValue, res)


def _createTable(name, colNames, colTypes, extraProperties, foreignKey = None, references = None):
    assert len(colNames) == len(colTypes)
    assert len(colNames) == len(extraProperties)

    return {
        "name": name,
        "colNames": colNames,
        "colTypes": colTypes,
        "extraProperties": extraProperties,
        "foreignKey": foreignKey,
        "references": references
    }


def defineTables():
    table_Teams = _createTable(name="Teams",
                               colNames=["teamId"],
                               colTypes=["int"],
                               extraProperties=["PRIMARY KEY"])

    table_Players = _createTable(name="Players",
                                 colNames=["playerId", "teamId", "age", "height", "preferredFoot"],
                                 colTypes=["int", "int", "int", "int", "varchar(255)"],
                                 extraProperties=["PRIMARY KEY", "NOT NULL", "NOT NULL", "NOT NULL", "NOT NULL"])
    table_Scores = _createTable(name="Scores",
                                colNames=["playerId", "matchId", "amount"],
                                colTypes=["int", "int", "int"],
                                extraProperties=["UNIQUE NOT NULL", "NOT NULL", "NOT NULL"])

    table_Matches = _createTable(name="Matches",
                                 colNames=["matchId", "competition", "homeTeamId", "awayTeamId"],
                                 colTypes=["int", "varchar(255)", "int", "int"],
                                 extraProperties=["UNIQUE NOT NULL", "NOT NULL", "NOT NULL", "NOT NULL"])

    table_MatchInStadium = _createTable(name="MatchInStadium",
                                        colNames=["matchId", "stadiumId", "attendance"],
                                        colTypes=["int", "int", "int"],
                                        extraProperties=["UNIQUE NOT NULL", "NOT NULL", "NOT NULL"])

    table_Stadiums = _createTable(name="Stadiums",
                                  colNames=["stadiumId", "capacity", "teamId"],
                                  colTypes=["int", "int", "int"],
                                  extraProperties=["UNIQUE NOT NULL", "NOT NULL", ""],
                                  foreignKey="teamId",
                                  references="Teams(teamId)")

    Tables.append(table_Teams)
    Tables.append(table_Players)
    Tables.append(table_Scores)
    Tables.append(table_Matches)
    Tables.append(table_MatchInStadium)
    Tables.append(table_Stadiums)


def defineViews():
    view_ActiveTallTeams = {
        "name": "",
        "query": "ActiveTallTeams",  # TODO
        "materialized": False
    }
    Views.append(view_ActiveTallTeams)

# endregion

# region Init
def createTables():

    defineTables()
    defineViews()

    # Table creator generator
    for table in Tables:
        q = "CREATE TABLE " + table["name"] + " ("
        for col_index in range(len(table["colNames"])):
            q += table["colNames"][col_index] + " " + table["colTypes"][col_index]
            q += " " + table["extraProperties"][col_index]
            if col_index < len(table["colNames"]) - 1:
                q += ", "

        if table["foreignKey"]:
            q += ", FOREIGN KEY ("+table["foreignKey"]+") REFERENCES "+table["references"]
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
    competiton = match.getCompetition()
    homeTeam = match.getHomeTeamID()
    awayTeam = match.getAwayTeamID()

    q = "INSERT INTO Matches (matchId ,competition, homeTeamId, awayTeamId) VALUES ("
    q += str(matchId) + " , '" + competiton + "' , " + str(homeTeam) + " , " + str(awayTeam) + " );"

    return sendQuery(q).Status



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
    q = "INSERT INTO players (playerId, teamId, age, height, preferredFoot) VALUES ("
    q += str(player.getPlayerID()) + ", "
    q += str(player.getTeamID()) + ", "
    q += str(player.getAge()) + ", "
    q += str(player.getHeight()) + ", "
    q += "'" + str(player.getFoot()) + "');"
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
    belongToIsNotNone = stadium.getBelongsTo() != None

    q = "INSERT INTO stadiums (stadiumId, capacity"
    if belongToIsNotNone:
        q += ", teamId"
    q += ") VALUES ("
    q += str(stadium.getStadiumID())
    q += ", " + str(stadium.getCapacity())
    if belongToIsNotNone:
        q += ", " + str(stadium.getBelongsTo())
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
    pass


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
