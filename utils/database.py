# -*- coding: utf-8 -*-

import sqlite3

database_file = "utils/database.db"

c = sqlite3.connect(database_file)
print "Opened database successfully"


class Database:

    def __init__(self):
        self.createTables()
        self.insertValues()
        self.closeDB()

    def createTables(self):
        try:
            c.execute('CREATE TABLE IF NOT EXISTS printView (element TEXT, value TEXT)')
            print "Table created successfully"
        except:
            pass



    def insertValues(self):
        try:
            # c.execute("INSERT INTO printView ('startButton') VALUES('test')")
            c.execute("INSERT INTO printView (element, value) VALUES(?, ?, ?, ?)", ("startButton", "j"), ("test", "fdg"))
            c.commit()
        except:
            pass

    def closeDB(self):
        try:
            c.close()
        except:
            pass