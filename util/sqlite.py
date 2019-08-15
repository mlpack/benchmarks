'''
  @file sqlite.py
  @author Marcus Edel

  SQLite database driver.
'''

import sqlite3

'''
SQLite driver class to write the into a SQLite database.
'''
class Driver(object):
  def __init__(self, param):
    self.build = 1
    self.database = param["sqlite_database"]
    self.connection = None
    self.cursor = None

    self.connect()
    self.create_table()
    self.latest_build()

  def connect(self):
    self.connection = sqlite3.connect(self.database)
    self.connection.execute('pragma foreign_keys = on')
    self.cursor = self.connection.cursor()

  def create_table(self):
    comand = """
        CREATE TABLE IF NOT EXISTS results (
          id INTEGER PRIMARY KEY %s,
          build INTEGER NOT NULL,
          library TEXT NOT NULL,
          datasets TEXT NOT NULL,
          method TEXT NOT NULL,
          method_param TEXT NOT NULL,
          base_param TEXT NOT NULL,
          runtime REAL NOT NULL,
          result TEXT NOT NULL
        );
        """
    self.connection.executescript(comand % "AUTOINCREMENT")

  def latest_build(self):
    with self.connection:
      command = "SELECT build FROM results ORDER BY build DESC"
      self.cursor.execute(command)
      result = self.cursor.fetchall()

      if result:
        self.build = int(result[0][0]) + 1

  def update(self, library, method, datasets, method_param, base_param, result):
    self.connect()
    with self.connection:
      command = "INSERT INTO results VALUES (NULL,%s,%s,%s,%s,%s,%s,%s,%s)"

      runtime = 0
      if "runtime" in result:
        runtime = result["runtime"]

      self.cursor.execute(command % ('?', '?', '?', '?', '?', '?', '?', '?'),
        (self.build, str(library), str(datasets), str(method),
        str(method_param), str(base_param), runtime, str(result)))
      self.cursor.execute("SELECT last_insert_rowid()")
