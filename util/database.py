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
  Create a new build table.
  '''
  def CreateBuildTable(self):
    self.con.executescript("""
        CREATE TABLE IF NOT EXISTS builds (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          build TIMESTAMP NOT NULL,
          libary_id INTEGER NOT NULL,

          FOREIGN KEY(libary_id) REFERENCES builds(id) ON DELETE CASCADE
        );
        """)

  '''
  Create a new libraries table.
  '''
  def CreateLibrariesTable(self):
    self.con.executescript("""
        CREATE TABLE IF NOT EXISTS libraries (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL
        );
        """)

  '''
  Create a new datasets table.
  '''
  def CreateDatasetsTable(self):
    self.con.executescript("""
        CREATE TABLE IF NOT EXISTS datasets (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL UNIQUE,
          size INTEGER NOT NULL,
          attributes INTEGER NOT NULL,
          instances INTEGER NOT NULL,
          type TEXT NOT NULL
        );
        """)

  '''
  Create a new methods table.
  '''
  def CreateMethodsTable(self):
    self.con.executescript("""
        CREATE TABLE IF NOT EXISTS methods (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          parameters TEXT NOT NULL
        );
        """)

  '''
  Create a new results table.
  '''
  def CreateResultsTable(self):
    self.con.executescript("""
        CREATE TABLE IF NOT EXISTS results (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          build_id INTEGER NOT NULL,
          libary_id INTEGER NOT NULL,
          time REAL NOT NULL,
          var REAL NOT NULL,
          dataset_id INTEGER NOT NULL,
          method_id INTEGER NOT NULL,

          FOREIGN KEY(build_id) REFERENCES builds(id) ON DELETE CASCADE,
          FOREIGN KEY(libary_id) REFERENCES libraries(id) ON DELETE CASCADE,
          FOREIGN KEY(dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
          FOREIGN KEY(method_id) REFERENCES methods(id) ON DELETE CASCADE
        );
        """)

  '''
  Create a new build, libraries, datasets and results table.
  '''
  def CreateTables(self):
    self.CreateLibrariesTable()
    self.CreateBuildTable()
    self.CreateDatasetsTable()
    self.CreateMethodsTable()
    self.CreateResultsTable()

  '''
  Add a new build record to the builds table.
  '''
  def NewBuild(self, libaryId):
    with self.con:
      self.cur.execute("INSERT INTO builds VALUES (NULL,?, ?)", 
          (datetime.datetime.now(), libaryId))
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

  '''
  Get the libary id form the libraries table with the given name.

  @param name - The name of the library.
  @return The records.
  '''
  def GetLibrary(self, name):
    with self.con:
      self.cur.execute("SELECT id FROM libraries WHERE name='" + name + "'")
      return self.cur.fetchall()

  '''
  Add a new library record to the libraries table.

  @param name - The name of the library.
  @return The id of the new record in the libraries table.
  '''
  def NewLibrary(self, name):
    with self.con:
      self.cur.execute("INSERT INTO libraries VALUES (NULL,?)", (name,))
      self.cur.execute("SELECT last_insert_rowid()")
      return self.cur.fetchall()[0][0]

  '''
  Add a new result record to the results table.

  @param buildId - The id of the build.
  @param libaryId - The if ot the library.
  @param time - The mesured time of the build.
  @param var - The variance of the build.
  @param datasetId - The id of the dataset.
  '''
  def NewResult(self, buildId, libaryId, time, var, datasetId, methodId):
     with self.con:
      self.cur.execute("INSERT INTO results VALUES (NULL,?,?,?,?,?,?)", 
          (buildId, libaryId, time, var, datasetId, methodId))

  '''
  Get the method if from the methods table with the given name and parameters.

  @param name - The name of the method.
  @param parameters - The parameters of the method.
  @return the records.
  '''
  def GetMethod(self, name, parameters):
     with self.con:
      self.cur.execute("SELECT id FROM methods WHERE name='" + name + 
          "' AND parameters='" + parameters + "'")
      return self.cur.fetchall()

  '''
  Add a new method record to the methods table.

  @param name - The name of the method.
  @param parameters - The parameters of the method.
  @return the record id.
  '''
  def NewMethod(self, name, parameters):
    with self.con:
      self.cur.execute("INSERT INTO methods VALUES (NULL,?, ?)", 
          (name,parameters))
      self.cur.execute("SELECT last_insert_rowid()")
      return self.cur.fetchall()[0][0]

  '''
  Get the sum of the time column of all build of the given name.

  @param name - The name of the library.
  @return The sum of the time column.
  '''
  def GetResultsSum(self, name):
    libaryId = self.GetLibrary(name)[0][0]
    with self.con:
      self.cur.execute("SELECT id FROM builds WHERE libary_id=" + str(libaryId) + " ORDER BY build ASC")
      timeSummed = []
      for buildId in self.cur.fetchall(): 
        self.cur.execute("SELECT SUM(time) FROM results WHERE build_id=" + 
           str(buildId[0]))
        timeSummed.append(self.cur.fetchall()[0][0])
    return timeSummed
