'''
  @file mysql.py
  @author Marcus Edel

  MySQL database driver.
'''

import MySQLdb as mdb

'''
MySQL driver class to write the into a MySQL database.
'''
class Driver(object):
  def __init__(self, param):
    self.build = 1
    self.connection = None
    self.cursor = None

    self.host = param["mysql_host"]
    self.port = param["mysql_port"]
    self.user = param["mysql_user"]
    self.database = param["mysql_database"]
    self.password = param["mysql_password"]

    self.connect()
    self.create_table()
    self.latest_build()

  def connect(self):
    self.connection = mdb.connect(host=self.host, port=self.port,
      user=self.user, db=self.database, passwd=self.password)
    self.cursor = self.connection.cursor()
    self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

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
    self.cursor.execute(comand % "AUTOINCREMENT")

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
      self.cursor.execute("SELECT LAST_INSERT_ID()")
