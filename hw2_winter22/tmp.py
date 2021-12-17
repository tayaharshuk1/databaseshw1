from Utility.DBConnector import *
from Solution import *


def _nukeDB():
    defineTables()
    Tables.reverse()
    for table in Tables:
        dbConnector = Connector.DBConnector()
        q = "DROP TABLE " + table["name"]
        try:
            dbConnector.execute(query=q)
        except BaseException as e:
            print(e)
        finally:
            dbConnector.close()
    Tables.clear()

def _testDB():
    createTables()
    addTeam(1)
    origMatch = Match(1, "CTF", 2, 3)
    addMatch(origMatch)
    resMatch = getMatchProfile(1)
    # res1 = dbConnector.execute(query="Select * FROM Teams")
    clearTables()
    # res2 = dbConnector.execute(query="Select * FROM Teams")
    dropTables()


_nukeDB()

# _testDB()


print("end")