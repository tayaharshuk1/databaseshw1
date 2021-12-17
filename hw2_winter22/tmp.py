from Utility.DBConnector import *
from Solution import *


def _nukeDB():
    defineTables()
    dropTables()
    Tables.clear()

def _testDB():
    createTables()
    addTeam(1)
    origMatch = Match(1, "CTF", 2, 3)
    addMatch(origMatch)
    resMatch = getMatchProfile(1)
    res1 = dbConnector.execute(query="Select * FROM Teams")
    clearTables()
    res2 = dbConnector.execute(query="Select * FROM Teams")
    dropTables()


_nukeDB()
_testDB()


print("end")