import sqlite3 

 
db = sqlite3.connect('path to project')


c = db.cursor()

# check all table names
c.execute("SELECT name from sqlite_master where type='table'")
print(c.fetchall())

# grab schema of a table
c.execute("PRAGMA table_info(AAPL)")
print(c.fetchall())

# fetch rows from a table 
# c.execute("SELECT * FROM AAPL where pice > 115")
c.execute("SELECT * FROM AAPL")
print(c.fetchall())