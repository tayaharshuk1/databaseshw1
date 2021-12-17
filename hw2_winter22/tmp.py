from Utility.DBConnector import *
from Solution import *


def _nukeDB():
    defineTables()
    dropTables()

def _testDB():
    createTables()
    addTeam(1)
    res1 = dbConnector.execute(query="Select * FROM Teams")
    clearTables()
    res2 = dbConnector.execute(query="Select * FROM Teams")
    dropTables()


# _nukeDB()
_testDB()


print("end")