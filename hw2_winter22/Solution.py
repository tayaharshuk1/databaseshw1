from typing import List
import Utility.DBConnector as Connector
from Utility.ReturnValue import ReturnValue
from Utility.Exceptions import DatabaseException
from Business.Match import Match
from Business.Player import Player
from Business.Stadium import Stadium
from psycopg2 import sql


dbConnector = Connector.DBConnector()
Tables = []
Views = []

tableTemplate = {
    "name": "",
    "colNames": [],
    "colTypes": [],
    "colCanBeNull": []
}

viewTemplate = {
    "query": "",
    "materialized": False
}

def _createTable(name, colNames, colTypes, colCanBeNull):
    assert len(colNames) == len(colTypes)
    assert len(colNames) == len(colCanBeNull)

    return {
        "name": name,
        "colNames": colNames,
        "colTypes": colTypes,
        "colCanBeNull": colCanBeNull
    }

def defineTables():
    table_Teams = _createTable(name="Teams",
                               colNames=["teamId"],
                               colTypes=["varchar(255)"],
                               colCanBeNull=[False])

    table_Players = _createTable(name="Players",
                                 colNames=["playerId", "teamId", "age", "height", "preferredFoot"],
                                 colTypes=["int", "int", "int", "int", "varchar(255)"],
                                 colCanBeNull=[False, False, False, False, False])

    table_Scores = _createTable(name="Scores",
                                colNames=["playerId", "matchId", "amount"],
                                colTypes=["int", "int", "int"],
                                colCanBeNull=[False, False, False])

    table_Matches = _createTable(name="Matches",
                                 colNames=["matchId", "competition", "homeTeamId", "awayTeamId"],
                                 colTypes=["int", "varchar(255)", "int", "int"],
                                 colCanBeNull=[False, False, False, False])

    table_MatchInStadium = _createTable(name="MatchInStadium",
                                        colNames=["matchId", "stadiumId", "attendance"],
                                        colTypes=["int", "int", "int"],
                                        colCanBeNull=[False, False, False])

    table_Stadiums = _createTable(name="Stadiums",
                                  colNames=["stadiumId", "capacity", "teamId"],
                                  colTypes=["int", "int", "int"],
                                  colCanBeNull=[False, False, True])

    Tables.append(table_Teams)
    Tables.append(table_Players)
    Tables.append(table_Scores)
    Tables.append(table_Matches)
    Tables.append(table_MatchInStadium)
    Tables.append(table_Stadiums)


def createTables():
    defineTables()

    view_ActiveTallTeams = {
        "name": "",
        "query": "ActiveTallTeams", # TODO
        "materialized": False
    }
    Views.append(view_ActiveTallTeams)

    # Table creator generator
    for table in Tables:
        q = "CREATE TABLE " + table["name"] + " ("
        for col_index in range(len(table["colNames"])):
            q += table["colNames"][col_index] + " " + table["colTypes"][col_index]
            if not table["colCanBeNull"][col_index]:
                q += " NOT NULL"
            if col_index < len(table["colNames"]) - 1 :
                q += ", "
        q += ")"

        try:
            dbConnector.execute(query=q)
        except BaseException as e:
            print(e)

    for view in Views:
        pass    # TODO : Jonathan

def clearTables():
    for table in Tables:
        q = "DELETE FROM " + table["name"]
        try:
            dbConnector.execute(query=q)
        except BaseException as e:
            print(e)


def dropTables():
    for table in Tables:
        q = "DROP TABLE " + table["name"]
        try:
            dbConnector.execute(query=q)
        except BaseException as e:
            print(e)


def _errorHandling(e) -> ReturnValue:
    pass

def addTeam(teamID: int) -> ReturnValue:
    q = "INSERT INTO Teams (teamId) VALUES (" + str(teamID) + ");"
    try:
        res = dbConnector.execute(query=q)
    except DatabaseException.CHECK_VIOLATION as e:
        return _errorHandling(e)

    return ReturnValue.OK



def addMatch(match: Match) -> ReturnValue:
    matchId = match.getMatchID()
    competiton = match.getCompetition()
    homeTeam =match.getHomeTeamID()
    awayTeam = match.getAwayTeamID()

    q = "INSERT INTO Matches (matchId ,competition, homeTeamId,awayTeamId) VALUES ("
    q+= str(matchId) + " , " +competiton + " , " + str(homeTeam) + " , " + str(awayTeam) + " );"
    try:
        res = dbConnector.execute(query=q)
    except DatabaseException.CHECK_VIOLATION as e:
        return _errorHandling(e)

    return ReturnValue.OK



def getMatchProfile(matchID: int) -> Match:
    pass    # TODO: Taya


def deleteMatch(match: Match) -> ReturnValue:
    pass    # TODO: Taya


def addPlayer(player: Player) -> ReturnValue:
    pass    # TODO: Taya


def getPlayerProfile(playerID: int) -> Player:
    pass   # TODO: Taya


def deletePlayer(player: Player) -> ReturnValue:
    pass    # TODO: Taya


def addStadium(stadium: Stadium) -> ReturnValue:
    pass


def getStadiumProfile(stadiumID: int) -> Stadium:
    pass


def deleteStadium(stadium: Stadium) -> ReturnValue:
    pass


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
    res = dbConnector.execute(query=q)

    rows = res[1].rows
    playerRow = rows[0]
    totalRow = rows[1]
    playerAmount = playerRow[0]
    totalAmount = totalRow[0]
    return 2*playerAmount >= totalAmount

def getAllTallActiveTeamsQuery():
    activeTeamsQ = ""   # TODO
    tallTeamsQ = ""     # TODO
    q = activeTeamsQ + " INTERSECT " + tallTeamsQ
    return q

def getActiveTallTeams() -> List[int]:
    q = getAllTallActiveTeamsQuery() + " ORDER BY teamId DESC LIMIT 5"

    res = dbConnector.execute(query=q)
    teams = []
    for row in res[1]:
        teams.append(row[0])
        # TODO: check of int

    return teams


def getActiveTallRichTeams() -> List[int]:
    activeTallTeamsQ = getAllTallActiveTeamsQuery()
    reachTeams = " " #TODO
    q = activeTallTeamsQ + " INTERSECT " + reachTeams + " ORDER BY teamId ASC LIMIT 5"

    res = dbConnector.execute(query=q)
    teams = []
    for row in res[1]:
        teams.append(row[0])
        # TODO: check of int

    return teams


def popularTeams() -> List[int]:
    pass


def getMostAttractiveStadiums() -> List[int]:
    pass


def mostGoalsForTeam(teamID: int) -> List[int]:
    pass


def getClosePlayers(playerID: int) -> List[int]:
    pass
