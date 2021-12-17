from Utility.DBConnector import *


dbConnector = DBConnector(section='tmp')

queryCreateTable = "CREATE TABLE students (name varchar(255), id int)"

queryAddRow = "INSERT INTO students (name, id) VALUES ('Taya', 1);"
queryAddRow2 = "INSERT INTO students (name, id) VALUES ('Jonathan', 2);"

queryRead = "SELECT name, id FROM students"

# createRes = dbConnector.execute(query=queryCreateTable)

# writeRes = dbConnector.execute(query=queryAddRow)
# writeRes2 = dbConnector.execute(query=queryAddRow2)

readRes = dbConnector.execute(query=queryRead)

dbConnector.close()

students = {}

for row in readRes[1].rows:
    students[row[1]] = row[0]

print(students)
print('end')