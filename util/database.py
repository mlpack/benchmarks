'''
  @file database.py
  @author Marcus Edel

  Class to handle the database.
'''

import sqlite3
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
    con = sqlite3.connect(databasePath)
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

          FOREIGN KEY(libary_id) REFERENCES libraries(id) ON DELETE CASCADE
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
          parameters TEXT NOT NULL,
          alias TEXT NOT NULL
        );
        """)
    # Update methods table schema.
    try:
      self.cur.execute("SELECT alias FROM methods")
      self.cur.fetchall()
    except sqlite3.OperationalError as e:
      self.cur.execute("ALTER TABLE methods ADD COLUMN alias TEXT");
      self.cur.fetchall()

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
  Create a new metric results table
  '''
  def CreateMetricResultsTable(self):
    self.con.executescript("""
        CREATE TABLE IF NOT EXISTS metrics (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          build_id INTEGER NOT NULL,
          libary_id INTEGER NOT NULL,
          metric TEXT NOT NULL,
          dataset_id INTEGER NOT NULL,
          method_id INTEGER NOT NULL,

          FOREIGN KEY(build_id) REFERENCES builds(id) ON DELETE CASCADE,
          FOREIGN KEY(libary_id) REFERENCES libraries(id) ON DELETE CASCADE,
          FOREIGN KEY(dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
          FOREIGN KEY(method_id) REFERENCES methods(id) ON DELETE CASCADE
        );
        """)

  '''
  Create a new metric results table
  '''
  def CreateMetricBootstrapTable(self):
    self.con.executescript("""
        CREATE TABLE IF NOT EXISTS bootstrap (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          build_id INTEGER NOT NULL,
          libary_id INTEGER NOT NULL,
          metric TEXT NOT NULL,
          dataset_id INTEGER NOT NULL,
          method_id INTEGER NOT NULL,

          FOREIGN KEY(build_id) REFERENCES builds(id) ON DELETE CASCADE,
          FOREIGN KEY(libary_id) REFERENCES libraries(id) ON DELETE CASCADE,
          FOREIGN KEY(dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
          FOREIGN KEY(method_id) REFERENCES methods(id) ON DELETE CASCADE
        );
        """)

  '''
  Create a new memory table.
  '''
  def CreateMemoryTable(self):
    self.con.executescript("""
        CREATE TABLE IF NOT EXISTS memory (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          build_id INTEGER NOT NULL,
          libary_id INTEGER NOT NULL,
          method_id INTEGER NOT NULL,
          dataset_id INTEGER NOT NULL,
          memory_info TEXT NOT NULL,

          FOREIGN KEY(build_id) REFERENCES builds(id) ON DELETE CASCADE,
          FOREIGN KEY(libary_id) REFERENCES libraries(id) ON DELETE CASCADE,
          FOREIGN KEY(dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
          FOREIGN KEY(method_id) REFERENCES methods(id) ON DELETE CASCADE
        );
        """)

    '''
  Create a method information table.
  '''
  def CreateMethodInfoTable(self):
    self.con.executescript("""
        CREATE TABLE IF NOT EXISTS method_info (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          method_id INTEGER NOT NULL,
          info TEXT NOT NULL,

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
    self.CreateMetricResultsTable()
    self.CreateMemoryTable()
    self.CreateMethodInfoTable()
    self.CreateMetricBootstrapTable()

  '''
  Add a new build record to the builds table.

  @param libaryId - The id of the library.
  @return The new build id.
  '''
  def NewBuild(self, libaryId):
    with self.con:
      self.cur.execute("INSERT INTO builds VALUES (NULL,?, ?)",
          (datetime.datetime.now(), libaryId))
      self.cur.execute("SELECT last_insert_rowid()")
      return self.cur.fetchall()[0][0]

  '''
  Add a new metrics result record to the metric table.
  @param buildId - The id of the build.
  @param libaryId - The if ot the library.
  @param metric - The metric result as string.
  @param datasetId - The id of the dataset.
  @param methodId - The id of the method.
  '''
  def NewMetricResult(self, buildId, libaryId, metric, datasetId, methodId):
    with self.con:
      self.cur.execute("INSERT INTO metrics VALUES (NULL,?,?,?,?,?)",
          (buildId, libaryId, str(metric), datasetId, methodId))

  '''
  Add a new metric result record to the bootstrap table.
  @param buildId - The id of the build.
  @param libaryId - The if ot the library.
  @param metric - The metric result as string.
  @param datasetId - The id of the dataset.
  @param methodId - The id of the method.
  '''
  def NewBootstrapResult(self, buildId, libaryId, metric, datasetId, methodId):
    with self.con:
      self.cur.execute("INSERT INTO bootstrap VALUES (NULL,?,?,?,?,?)",
          (buildId, libaryId, str(metric), datasetId, methodId))


  def UpdateMetricResult(self, buildId, libaryId, metric, datasetId, methodId):
    with self.con:
      if self.GetMetricResult(buildId, libaryId, datasetId, methodId):
        self.cur.execute("UPDATE metrics SET metric='" + str(metric) + "'"
            + " WHERE build_id=" + str(buildId) + " AND libary_id="
            + str(libaryId) + " AND dataset_id=" + str(datasetId)
            + " AND method_id=" + str(methodId))
      else:
        self.NewMetricResult(buildId, libaryId, metric, datasetId, methodId)

  def UpdateBootstrapResult(self, buildId, libaryId, metric, datasetId, methodId):
    with self.con:
      if self.GetBootstrapResult(buildId, libaryId, datasetId, methodId):
        self.cur.execute("UPDATE bootstrap SET metric='" + str(metric) + "'"
            + " WHERE build_id=" + str(buildId) + " AND libary_id="
            + str(libaryId) + " AND dataset_id=" + str(datasetId)
            + " AND method_id=" + str(methodId))
      else:
        self.NewBootstrapResult(buildId, libaryId, metric, datasetId, methodId)

  def GetMetricResult(self, buildId, libaryId, datasetId, methodId):
    with self.con:
      self.cur.execute("SELECT * FROM metrics WHERE build_id=" + str(buildId)
          + " AND libary_id=" + str(libaryId) + " AND dataset_id="
          + str(datasetId) + " AND method_id=" + str(methodId))
      return self.cur.fetchall()

  def GetBootstrapResult(self, buildId, libaryId, datasetId, methodId):
    with self.con:
      self.cur.execute("SELECT * FROM bootstrap WHERE build_id=" + str(buildId)
          + " AND libary_id=" + str(libaryId) + " AND dataset_id="
          + str(datasetId) + " AND method_id=" + str(methodId))
      return self.cur.fetchall()

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

  @param id - The id of the build.
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
  @param methodId - The id of the method.
  '''
  def NewResult(self, buildId, libaryId, time, var, datasetId, methodId):
    with self.con:
      self.cur.execute("INSERT INTO results VALUES (NULL,?,?,?,?,?,?)",
        (buildId, libaryId, time, var, datasetId, methodId))

  '''
  Get the specified result from the results table.

  @param buildId - The id of the build.
  @param libaryId - The if ot the library.
  @param datasetId - The id of the dataset.
  @param methodId - The id of the method.
  @return The specified result record.
  '''
  def GetResult(self, buildId, libaryId, datasetId, methodId):
    with self.con:
      self.cur.execute("SELECT * FROM results WHERE build_id=" + str(buildId)
          + " AND libary_id=" + str(libaryId) + " AND dataset_id="
          + str(datasetId) + " AND method_id=" + str(methodId))
      return self.cur.fetchall()

  '''
  Update the given result record in the results table if the record is available
  otherwise create a new record.

  @param buildId - The id of the build.
  @param libaryId - The if ot the library.
  @param time - The mesured time of the build.
  @param var - The variance of the build.
  @param datasetId - The id of the dataset.
  @param methodId - The id of the method.
  '''
  def UpdateResult(self, buildId, libaryId, time, var, datasetId, methodId):
    with self.con:
      if self.GetResult(buildId, libaryId, datasetId, methodId):
        self.cur.execute("UPDATE results SET time=" + str(time) + ",var="
            + str(var) + " WHERE build_id=" + str(buildId) + " AND libary_id="
            + str(libaryId) + " AND dataset_id=" + str(datasetId)
            + " AND method_id=" + str(methodId))
      else:
        self.NewResult(buildId, libaryId, time, var, datasetId, methodId)

  '''
  Get the method id from the methods table with the given name and parameters.

  @param name - The name of the method.
  @param parameters - The parameters of the method.
  @return The records.
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
  @param alias - The alias of the method parameter combination.
  @return The record id.
  '''
  def NewMethod(self, name, parameters, alias):
    with self.con:
      self.cur.execute("INSERT INTO methods VALUES (NULL,?, ?,?)",
          (name, parameters, alias))
      self.cur.execute("SELECT last_insert_rowid()")
      return self.cur.fetchall()[0][0]

  def UpdateMethod(self, methodId, alias):
    self.cur.execute("UPDATE methods SET alias=\'" + alias + "\' WHERE id="
        + str(methodId))

  '''
  Get the sum of the time column of all build of the given name.

  @param name - The name of the library.
  @return The sum of the time column if there are records otherwise None.
  '''
  def GetResultsSum(self, name):
    libaryId = self.GetLibrary(name)
    if libaryId:
      libaryId = libaryId[0][0]
    else:
      return None

    with self.con:
      self.cur.execute("SELECT id FROM builds WHERE libary_id=" + str(libaryId)
          + " ORDER BY build ASC")
      timeSummed = []
      res = self.cur.fetchall()
      for buildId in res:
        self.cur.execute("SELECT SUM(time) FROM results WHERE build_id=" +
           str(buildId[0]))
        timeSummed.append(self.cur.fetchall()[0][0])
    if res:
      return (buildId[0], timeSummed)
    else:
      return None

  '''
  Get the ids of all libraries.

  @return The ids of the libraries.
  '''
  def GetLibraryIds(self):
    with self.con:
      self.cur.execute("SELECT * FROM libraries")
      return self.cur.fetchall()

  '''
  Get the latest build id for the specified libary id.

  @param libaryId - Get the build id for the libary id.
  @param The latest build id if there is a latest build otherwise -1.
  '''
  def GetLatestBuildFromLibary(self, libaryId):
    with self.con:
      self.cur.execute("SELECT id FROM builds WHERE libary_id=" + str(libaryId)
          + " ORDER BY build DESC")
      res = self.cur.fetchall()
      if res:
        return res
      else:
        return [(-1,)]

  def CopyLatestBuildFromLibary(self, buildId, newBuildId):
    self.cur.execute("SELECT * FROM results WHERE build_id=" + str(buildId))
    results = self.cur.fetchall()
    with self.con:
      for res in results:
        self.cur.execute("INSERT INTO results VALUES (NULL,?,?,?,?,?,?)",
            (newBuildId, res[2], res[3], res[4], res[5], res[6]))

  '''
  Get a list of all methods.

  @return A list with all methods.
  '''
  def GetAllMethods(self):
    with self.con:
      self.cur.execute("SELECT * FROM methods ORDER BY name ASC")
      return self.cur.fetchall()

  '''
  Get the results for the specified method and build id.

  @param buildId - The build id.
  @param methodId - The method id.
  @return A list with the results.
  '''
  def GetMethodResultsForLibary(self, buildId, methodId):
    with self.con:
      self.cur.execute("SELECT * FROM results JOIN datasets ON" +
          " results.dataset_id = datasets.id WHERE build_id=" + str(buildId) +
          " AND method_id=" + str(methodId) + " ORDER BY datasets.name")
      return self.cur.fetchall()

  '''
  Get the metrics results for the specified method and build id.

  @param buildId - The build id.
  @param methodId - The method id.
  @return A list with the results.
  '''
  def GetMethodMetricResultsForLibrary(self, buildId, methodId):
    with self.con:
      self.cur.execute("SELECT * FROM metrics JOIN datasets ON" +
          " metrics.dataset_id = datasets.id WHERE build_id=" + str(buildId) +
          " AND method_id=" + str(methodId) + " ORDER BY datasets.name")
      return self.cur.fetchall()

  '''
  Get the bootstrap results for the specified method and build id.

  @param buildId - The build id.
  @param methodId - The method id.
  @return A list with the results.
  '''
  def GetMethodBootstrapResultsForLibrary(self, buildId, methodId):
    with self.con:
      self.cur.execute("SELECT * FROM bootstrap JOIN datasets ON" +
          " bootstrap.dataset_id = datasets.id WHERE build_id=" + str(buildId) +
          " AND method_id=" + str(methodId) + " ORDER BY datasets.name")
      return self.cur.fetchall()

  '''
  Get the sum of the time column of all build of the given method.

  @param name - The name of the library.
  @param methodId - The method id.
  @return The sum of the time column if there are records otherwise None.
  '''
  def GetResultsMethodSum(self, name, methodId):
    if not self.GetLibrary(name):
      return None
    libaryId = self.GetLibrary(name)[0][0]
    with self.con:
      self.cur.execute("SELECT id FROM builds WHERE libary_id=" + str(libaryId)
          + " ORDER BY build ASC")
      timeSummed = []
      res = self.cur.fetchall()
      for buildId in res:
        self.cur.execute("SELECT SUM(time) FROM results WHERE build_id=" +
           str(buildId[0]) + " AND method_id=" + str(methodId))
        timeSummed.append(self.cur.fetchall()[0][0])
    if res:
      return (buildId[0], timeSummed)
    else:
      return None

  '''
  Add a new memory record to the memory table.

  @param buildId - The build id.
  @param libaryId - The id of the library.
  @param methodId - The id of the method
  @param datasetId - The id of the dataset.
  @param memoryInfo - The text for the memory value.
  '''
  def NewMemory(self, buildId, libaryId, methodId, datasetId, memoryInfo):
     with self.con:
      self.cur.execute("INSERT INTO memory VALUES (NULL,?,?,?,?,?)",
          (buildId, libaryId, methodId, datasetId, memoryInfo))

  '''
  Update the given memory record in the memory table if the record is available
  otherwise create a new record.

  @param buildId - The build id.
  @param libaryId - The id of the library.
  @param methodId - The id of the method
  @param datasetId - The id of the dataset.
  @param memoryInfo - The text for the memory value.
  '''
  def UpdateMemory(self, buildId, libaryId, methodId, datasetId, memoryInfo):
     with self.con:

      if self.GetMemoryResults(buildId, libaryId, methodId):
        self.cur.execute("UPDATE memory SET memory_info=\'" + memoryInfo
          + "\' WHERE build_id=" + str(buildId) + " AND libary_id="
          + str(libaryId) + " AND dataset_id=" + str(datasetId)
          + " AND method_id=" + str(methodId))
      else:
        self.NewMemory(buildId, libaryId, methodId, datasetId, memoryInfo)

  '''
  Get the memory informations of the given parameters.

  @param buildId - The id of the build.
  @param libaryId - The id of the library.
  @param methodId - The id of the method.
  @return The memory informations of the method.
  '''
  def GetMemoryResults(self, buildId, libaryId, methodId):
    with self.con:
      self.cur.execute("SELECT * FROM memory JOIN datasets ON " +
        "memory.dataset_id = datasets.id WHERE libary_id=" + str(libaryId) +
        " AND build_id="+ str(buildId) + " AND method_id=" + str(methodId))
      return self.cur.fetchall()

  '''
  Get the information of the given method.

  @param methodId - The id of the method.
  @return The informaton of the method.
  '''
  def GetMethodInfo(self, methodId):
    with self.con:
      self.cur.execute("SELECT * FROM method_info WHERE method_id=" +
          str(methodId))
      return self.cur.fetchall()

  '''
  Add a new method info record to the method_info table.

  @param methodId - The id of the method.
  @param info - The info for the method.
  '''
  def NewMethodInfo(self, methodId, info):
    with self.con:
      self.cur.execute("INSERT INTO method_info VALUES (NULL,?,?)",
        (methodId, info))

  '''
  Get the parameters of a given method.

  @param methodId - The id of the method.
  @return The parameters of the method.
  '''
  def GetMethodParameters(self, methodId):
    with self.con:
      self.cur.execute("SELECT parameters FROM methods WHERE id=" +
          str(methodId))
      return self.cur.fetchall()
