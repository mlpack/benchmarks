'''
  @file database.py
  @author Marcus Edel

  Class to handle the database.
'''

import sqlite3 as lite
import datetime


'''
This class implements functions to handle the database.
'''
class Database:

  '''
  Open the database connection.

  @param databasePath - Path to the database.
  '''
  def __init__(self, databasePath="benchmark.db"):
    con = lite.connect(databasePath)
    con.execute('pragma foreign_keys = on')

    self.con = con
    self.cur = con.cursor()

  '''
  Create a new build table (remove the existing table).
  '''
  def CreateBuildTable(self):
    self.con.executescript("""
        DROP TABLE IF EXISTS builds;
        CREATE TABLE builds (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          build TIMESTAMP NOT NULL
        );
        """)

  '''
  Create a new libraries table (remove the existing table).
  '''
  def CreateLibrariesTable(self):
    self.con.executescript("""
        DROP TABLE IF EXISTS libraries;
        CREATE TABLE libraries (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL
        );
        """)

  '''
  Create a new datasets table (remove the existing table).
  '''
  def CreateDatasetsTable(self):
    self.con.executescript("""
        DROP TABLE IF EXISTS datasets;
        CREATE TABLE datasets (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL UNIQUE,
          size INTEGER NOT NULL,
          attributes INTEGER NOT NULL,
          instances INTEGER NOT NULL,
          type TEXT NOT NULL
        );
        """)

  '''
  Create a new results table (remove the existing table).
  '''
  def CreateResultsTable(self):
    self.con.executescript("""
        DROP TABLE IF EXISTS results;
        CREATE TABLE results (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          build_id INTEGER NOT NULL,
          libary_id INTEGER NOT NULL,
          time REAL NOT NULL,
          var REAL NOT NULL,
          dataset_id INTEGER NOT NULL,

          FOREIGN KEY(build_id) REFERENCES builds(id) ON DELETE CASCADE,
          FOREIGN KEY(libary_id) REFERENCES libraries(id) ON DELETE CASCADE,
          FOREIGN KEY(dataset_id) REFERENCES datasets(id) ON DELETE CASCADE
        );
        """)

  '''
  Create a new build, libraries, datasets and results table.
  '''
  def CreateTables(self):
    self.CreateBuildTable()
    self.CreateLibrariesTable()
    self.CreateDatasetsTable()
    self.CreateResultsTable()

  '''
  Add a new build record to the builds table.
  '''
  def NewBuild(self):
    with self.con:
      self.cur.execute("INSERT INTO builds VALUES(NULL, '" + 
          str(datetime.datetime.now()) + "')")
      self.cur.execute("SELECT last_insert_rowid()")
      return self.cur.fetchall()[0][0]

  '''
  Add a new dataset record to the datasets table.

  @param name - The name of the dataset.
  @param size - The size of the dataset.
  @param attributes - Attributes count.
  @param instances - Instances count.
  @param datasetType - Type of the dataset.
  @return The id of the new record in the datasets table.
  '''
  def NewDataset(self, name, size, attributes, instances, datasetType="real"):
    with self.con:
      self.cur.execute("INSERT INTO datasets VALUES (NULL,?,?,?,?,?)", 
          (name, size, attributes, instances, datasetType))
      self.cur.execute("SELECT last_insert_rowid()")
      return self.cur.fetchall()[0][0]

  '''
  Get the informations of the given dataset.

  @param name - The name of the dataset.
  @return The records.
  '''
  def GetDataset(self, name):
    with self.con:
      self.cur.execute("SELECT id FROM datasets WHERE name='" + name  + "'")
      return self.cur.fetchall()

  '''
  Get the informations of the given build.

  @param id - The if of the build.
  @return The records.
  '''
  def GetBuild(self, id):
    with self.con:
      self.cur.execute("SELECT * FROM results WHERE build_id=" + str(id))
      return self.cur.fetchall()
