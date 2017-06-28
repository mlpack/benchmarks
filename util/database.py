'''
  @file database.py
  @author Marcus Edel

  Class to handle the database.
'''

# Import the sqlite3 python package.
try:
  import sqlite3
except ImportError:
  pass

# Import the mysql python package.
try:
  import MySQLdb as mdb
except ImportError:
  pass

import datetime
import json

'''
This class implements functions to handle the database.
'''
class Database:

  '''
  Open the database connection.

  @param driver - Driver used for the connection (mysql or sqlite).
  @param database - Path to the database or databse name.
  @param host - The hostname used for the mysql connection.
  @param user - The username used for the mysql connection.
  @param password - The password used for the mysql connection.
  '''
  def __init__(self, driver="sqlite", database="benchmark.db",
      host="localhost", user=None, password=None, port=3306):
    self.con = None
    self.cur = None
    self.driver = driver

    self.host = host
    self.port = port
    self.user = user
    self.database = database
    self.password = password
    self.driver = driver
    self.error = 0

    if driver == "mysql":
      self.con = mdb.connect(host=host, port=port, user=user, db=database, passwd=password)
      self.cur = self.con.cursor()
      self.cur.execute('SET FOREIGN_KEY_CHECKS = 0')

    elif driver == "sqlite":
      self.con = sqlite3.connect(database)
      self.con.execute('pragma foreign_keys = on')
      self.cur = self.con.cursor()

  '''
  Create a new build table.
  '''
  def CreateBuildTable(self):
    comand = """
        CREATE TABLE IF NOT EXISTS builds (
          id INTEGER PRIMARY KEY %s,
          build TIMESTAMP NOT NULL,
          libary_id INTEGER NOT NULL,

          FOREIGN KEY(libary_id) REFERENCES libraries(id) ON DELETE CASCADE
        );
        """

    if self.driver == "mysql":
      self.cur.execute(comand % "AUTO_INCREMENT")
    elif self.driver == "sqlite":
      self.con.executescript(comand % "AUTOINCREMENT")

  '''
  Create a new libraries table.
  '''
  def CreateLibrariesTable(self):
    comand = """
        CREATE TABLE IF NOT EXISTS libraries (
          id INTEGER PRIMARY KEY %s,
          name TEXT NOT NULL
        );
        """

    if self.driver == "mysql":
      self.cur.execute(comand % "AUTO_INCREMENT")
    elif self.driver == "sqlite":
      self.con.executescript(comand % "AUTOINCREMENT")

  '''
  Create a new datasets table.
  '''
  def CreateDatasetsTable(self):
    comand = """
        CREATE TABLE IF NOT EXISTS datasets (
          id INTEGER PRIMARY KEY %s,
          name TEXT NOT NULL,
          size INTEGER NOT NULL,
          attributes INTEGER NOT NULL,
          instances INTEGER NOT NULL,
          type TEXT NOT NULL
        );
        """

    if self.driver == "mysql":
      self.cur.execute(comand % "AUTO_INCREMENT")
    elif self.driver == "sqlite":
      self.con.executescript(comand % "AUTOINCREMENT")

  '''
  Create a new methods table.
  '''
  def CreateMethodsTable(self):
    comand = """
        CREATE TABLE IF NOT EXISTS methods (
          id INTEGER PRIMARY KEY %s,
          name TEXT NOT NULL,
          parameters TEXT NOT NULL,
          alias TEXT NOT NULL
        );
        """

    if self.driver == "mysql":
      self.cur.execute(comand % "AUTO_INCREMENT")
    elif self.driver == "sqlite":
      self.con.executescript(comand % "AUTOINCREMENT")
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
    comand = """
        CREATE TABLE IF NOT EXISTS results (
          id INTEGER PRIMARY KEY %s,
          build_id INTEGER NOT NULL,
          libary_id INTEGER NOT NULL,
          time REAL NOT NULL,
          var REAL NOT NULL,
          dataset_id INTEGER NOT NULL,
          method_id INTEGER NOT NULL,
          sweep_id INTEGER NOT NULL,
          sweep_elem_id INTEGER NOT NULL,

          FOREIGN KEY(build_id) REFERENCES builds(id) ON DELETE CASCADE,
          FOREIGN KEY(libary_id) REFERENCES libraries(id) ON DELETE CASCADE,
          FOREIGN KEY(dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
          FOREIGN KEY(method_id) REFERENCES methods(id) ON DELETE CASCADE
        );
        """

    if self.driver == "mysql":
      self.cur.execute(comand % "AUTO_INCREMENT")
    elif self.driver == "sqlite":
      self.con.executescript(comand % "AUTOINCREMENT")

  '''
  Create a new metric results table
  '''
  def CreateMetricResultsTable(self):
    comand = """
        CREATE TABLE IF NOT EXISTS metrics (
          id INTEGER PRIMARY KEY %s,
          build_id INTEGER NOT NULL,
          libary_id INTEGER NOT NULL,
          metric TEXT NOT NULL,
          dataset_id INTEGER NOT NULL,
          method_id INTEGER NOT NULL,
          sweep_id INTEGER NOT NULL,
          sweep_elem_id INTEGER NOT NULL,

          FOREIGN KEY(build_id) REFERENCES builds(id) ON DELETE CASCADE,
          FOREIGN KEY(libary_id) REFERENCES libraries(id) ON DELETE CASCADE,
          FOREIGN KEY(dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
          FOREIGN KEY(method_id) REFERENCES methods(id) ON DELETE CASCADE
        );
        """

    if self.driver == "mysql":
      self.cur.execute(comand % "AUTO_INCREMENT")
    elif self.driver == "sqlite":
      self.con.executescript(comand % "AUTOINCREMENT")

  '''
  Create a new metric results table
  '''
  def CreateMetricBootstrapTable(self):
    comand = """
        CREATE TABLE IF NOT EXISTS bootstrap (
          id INTEGER PRIMARY KEY %s,
          build_id INTEGER NOT NULL,
          libary_id INTEGER NOT NULL,
          metric TEXT NOT NULL,
          dataset_id INTEGER NOT NULL,
          method_id INTEGER NOT NULL,
          sweep_id INTEGER NOT NULL,
          sweep_elem_id INTEGER NOT NULL,

          FOREIGN KEY(build_id) REFERENCES builds(id) ON DELETE CASCADE,
          FOREIGN KEY(libary_id) REFERENCES libraries(id) ON DELETE CASCADE,
          FOREIGN KEY(dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
          FOREIGN KEY(method_id) REFERENCES methods(id) ON DELETE CASCADE
        );
        """

    if self.driver == "mysql":
      self.cur.execute(comand % "AUTO_INCREMENT")
    elif self.driver == "sqlite":
      self.con.executescript(comand % "AUTOINCREMENT")

  '''
  Create a new memory table.
  '''
  def CreateMemoryTable(self):
    comand = """
        CREATE TABLE IF NOT EXISTS memory (
          id INTEGER PRIMARY KEY %s,
          build_id INTEGER NOT NULL,
          libary_id INTEGER NOT NULL,
          method_id INTEGER NOT NULL,
          dataset_id INTEGER NOT NULL,
          memory_info TEXT NOT NULL,
          sweep_id INTEGER NOT NULL,
          sweep_elem_id INTEGER NOT NULL,

          FOREIGN KEY(build_id) REFERENCES builds(id) ON DELETE CASCADE,
          FOREIGN KEY(libary_id) REFERENCES libraries(id) ON DELETE CASCADE,
          FOREIGN KEY(dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
          FOREIGN KEY(method_id) REFERENCES methods(id) ON DELETE CASCADE
        );
        """

    if self.driver == "mysql":
      self.cur.execute(comand % "AUTO_INCREMENT")
    elif self.driver == "sqlite":
      self.con.executescript(comand % "AUTOINCREMENT")

  '''
  Create a method information table.
  '''
  def CreateMethodInfoTable(self):
    comand = """
        CREATE TABLE IF NOT EXISTS method_info (
          id INTEGER PRIMARY KEY %s,
          method_id INTEGER NOT NULL,
          info TEXT NOT NULL,

          FOREIGN KEY(method_id) REFERENCES methods(id) ON DELETE CASCADE
        );
        """

    if self.driver == "mysql":
      self.cur.execute(comand % "AUTO_INCREMENT")
    elif self.driver == "sqlite":
      self.con.executescript(comand % "AUTOINCREMENT")

  '''
  Create a table to hold information about sweeps.
  '''
  def CreateSweepsTable(self):
    command = """
        CREATE TABLE IF NOT EXISTS sweeps (
          id INTEGER PRIMARY KEY %s,
          type TEXT NOT NULL,
          begin TEXT NOT NULL,
          step TEXT NOT NULL,
          end TEXT NOT NULL
        );
        """

    if self.driver == "mysql":
      self.cur.execute(command % "AUTO_INCREMENT")
    elif self.driver == "sqlite":
      self.con.executescript(command % "AUTOINCREMENT")

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
    self.CreateSweepsTable()

  '''
  Add a new build record to the builds table.

  @param libaryId - The id of the library.
  @return The new build id.
  '''
  def NewBuild(self, libaryId):
    with self.con:
      command = "INSERT INTO builds VALUES (NULL,%s,%s)"

      if self.driver == "mysql":
        self.cur.execute(command, (datetime.datetime.now(), libaryId))
        self.cur.execute("SELECT LAST_INSERT_ID()")

      elif self.driver == "sqlite":
        self.cur.execute(command % ('?', '?'),
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
  @param sweepId - The id of the sweep (-1 for no sweep).
  @param sweepElementId - The element id of the sweep (-1 for no sweep).
  '''
  def NewMetricResult(self, buildId, libaryId, metric, datasetId, methodId,
                      sweepId=-1, sweepElementId=-1):
    try:
      with self.con:
        command = "INSERT INTO metrics VALUES (NULL,%s,%s,%s,%s,%s,%s,%s)"

        if self.driver == "mysql":
          self.cur.execute(command,
              (buildId, libaryId, str(metric), datasetId, methodId, sweepId,
               sweepElementId))

        elif self.driver == "sqlite":
          self.cur.execute(command % ('?', '?', '?', '?', '?', '?', '?'),
              (buildId, libaryId, str(metric), datasetId, methodId, sweepId,
               sweepElementId))

        self.error = 0
    except Exception:
      if self.error == 0:
        self.error = 1
        self.con = mdb.connect(host=self.host, port=self.port, user=self.user, db=self.database, passwd=self.password)
        self.cur = self.con.cursor()
        self.cur.execute('SET FOREIGN_KEY_CHECKS = 0')

        self.NewMetricResult(buildId, libaryId, metric, datasetId, methodId,
                             sweepId, sweepElementId)

  '''
  Add a new metric result record to the bootstrap table.
  @param buildId - The id of the build.
  @param libaryId - The if ot the library.
  @param metric - The metric result as string.
  @param datasetId - The id of the dataset.
  @param methodId - The id of the method.
  @param sweepId - The id of the sweep (-1 if no sweep).
  @param sweepElementId - The element id of the sweep (-1 if no sweep).
  '''
  def NewBootstrapResult(self, buildId, libaryId, metric, datasetId, methodId,
                         sweepId=-1, sweepElementId=-1):
    with self.con:
      command = "INSERT INTO bootstrap VALUES (NULL,%s,%s,%s,%s,%s,%s,%s)"

      if self.driver == "mysql":
        self.cur.execute(command,
            (buildId, libaryId, str(metric), datasetId, methodId, sweepId,
             sweepElementId))

      elif self.driver == "sqlite":
        self.cur.execute(command % ('?', '?', '?', '?', '?', '?', '?'),
            (buildId, libaryId, str(metric), datasetId, methodId, sweepId,
             sweepElementId))

  '''
  Create a new sweep.

  @param sweepType Type of the sweep ('float' or 'int'), a string.
  @param sweepBegin First value of the sweep.
  @param sweepStep Step size of the sweep.
  @param sweepEnd Final value of the sweep.
  '''
  def NewSweep(self, sweepType, sweepBegin, sweepStep, sweepEnd):
    with self.con:
      command = "INSERT INTO sweeps VALUES (NULL, %s, %s, %s, %s)"

      if self.driver == "mysql":
        self.cur.execute(command, (sweepType, sweepBegin, sweepStep, sweepEnd))
        self.cur.execute("SELECT LAST_INSERT_ID()")
      elif self.driver == "sqlite":
        self.cur.execute(command % ('?', '?', '?', '?'),
            (sweepType, sweepBegin, sweepStep, sweepEnd))
        self.cur.execute("SELECT last_insert_rowid()")

      return self.cur.fetchall()[0][0]

  def UpdateMetricResult(self, buildId, libaryId, metric, datasetId, methodId,
                         sweepId=-1, sweepElementId=-1):
    with self.con:
      if self.GetMetricResult(buildId, libaryId, datasetId, methodId, sweepId,
                              sweepElementId):
        if sweepId != -1:
          self.cur.execute("UPDATE metrics SET metric='" + str(metric) + "'"
              + " WHERE build_id=" + str(buildId) + " AND libary_id="
              + str(libaryId) + " AND dataset_id=" + str(datasetId)
              + " AND method_id=" + str(methodId))
        else:
          self.cur.execute("UPDATE metrics SET metric='" + str(metric) + "'"
              + " WHERE build_id=" + str(buildId) + " AND libary_id="
              + str(libaryId) + " AND dataset_id=" + str(datasetId)
              + " AND method_id=" + str(methodId) + " AND sweep_id="
              + str(sweepId) + " AND sweep_element_id=" + str(sweepElementId))
      else:
        self.NewMetricResult(buildId, libaryId, metric, datasetId, methodId,
                             sweepId, sweepElementId)

  def UpdateBootstrapResult(self, buildId, libaryId, metric, datasetId,
                            methodId, sweepId=-1, sweepElementId=-1):
    with self.con:
      if self.GetBootstrapResult(buildId, libaryId, datasetId, methodId,
                                 sweepId, sweepElementId):
        if sweepId == -1:
          self.cur.execute("UPDATE bootstrap SET metric='" + str(metric) + "'"
              + " WHERE build_id=" + str(buildId) + " AND libary_id="
              + str(libaryId) + " AND dataset_id=" + str(datasetId)
              + " AND method_id=" + str(methodId))
        else:
          self.cur.execute("UPDATE bootstrap SET metric='" + str(metric) + "'"
              + " WHERE build_id=" + str(buildId) + " AND libary_id="
              + str(libaryId) + " AND dataset_id=" + str(datasetId)
              + " AND method_id=" + str(methodId) + " AND sweepId="
              + str(sweepId) + " AND sweepElementId=" + str(sweepElementId))
      else:
        self.NewBootstrapResult(buildId, libaryId, metric, datasetId, methodId)

  def GetMetricResult(self, buildId, libaryId, datasetId, methodId, sweepId=-1,
                      sweepElementId=-1):
    try:
      with self.con:
        if sweepId == -1:
          self.cur.execute("SELECT * FROM metrics WHERE build_id=" + str(buildId)
              + " AND libary_id=" + str(libaryId) + " AND dataset_id="
              + str(datasetId) + " AND method_id=" + str(methodId))
        else:
          self.cur.execute("SELECT * FROM metrics WHERE build_id=" + str(buildId)
              + " AND libary_id=" + str(libaryId) + " AND dataset_id="
              + str(datasetId) + " AND method_id=" + str(methodId)
              + " AND sweepId=" + str(sweepId) + " AND sweepElementId="
              + str(sweepElementId))
        return self.cur.fetchall()
    except Exception:
      return None

  def GetBootstrapResult(self, buildId, libaryId, datasetId, methodId,
                         sweepId=-1, sweepElementId=-1):
    with self.con:
      if sweepId == -1:
        self.cur.execute("SELECT * FROM bootstrap WHERE build_id=" + str(buildId)
            + " AND libary_id=" + str(libaryId) + " AND dataset_id="
            + str(datasetId) + " AND method_id=" + str(methodId))
      else:
        self.cur.execute("SELECT * FROM bootstrap WHERE build_id=" + str(buildId)
            + " AND libary_id=" + str(libaryId) + " AND dataset_id="
            + str(datasetId) + " AND method_id=" + str(methodId)
            + " AND sweep_id=" + str(sweepId) + " AND sweep_element_id="
            + str(sweepElementId))
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
      command = "INSERT INTO datasets VALUES (NULL,%s,%s,%s,%s,%s)"

      if self.driver == "mysql":
        self.cur.execute(command,
            (name, size, attributes, instances, datasetType))
        self.cur.execute("SELECT LAST_INSERT_ID()")

      elif self.driver == "sqlite":
        self.cur.execute(command % ('?', '?', '?', '?', '?'),
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
      command = "INSERT INTO libraries VALUES (NULL, %s)"

      if self.driver == "mysql":
        self.cur.execute(command, (name,))
        self.cur.execute("SELECT LAST_INSERT_ID()")

      elif self.driver == "sqlite":
        self.cur.execute(command % ('?'), (name,))
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
  @param sweepId - The id of the sweep (-1 if no sweep).
  @param sweepElementId - The element in the sweep (-1 if no sweep).
  '''
  def NewResult(self, buildId, libaryId, time, var, datasetId, methodId,
                sweepId=-1, sweepElementId=-1):
    with self.con:
      command = "INSERT INTO results VALUES (NULL,%s,%s,%s,%s,%s,%s,%s,%s)"

      if self.driver == "mysql":
        self.cur.execute(command,
            (buildId, libaryId, time, var, datasetId, methodId, sweepId,
             sweepElementId))
        self.cur.execute("SELECT LAST_INSERT_ID()")

      elif self.driver == "sqlite":
        self.cur.execute(command % ('?', '?', '?', '?', '?', '?', '?', '?'),
            (buildId, libaryId, time, var, datasetId, methodId, sweepId,
             sweepElementId))
        self.cur.execute("SELECT last_insert_rowid()")

  '''
  Get the specified result from the results table.

  @param buildId - The id of the build.
  @param libaryId - The if ot the library.
  @param datasetId - The id of the dataset.
  @param methodId - The id of the method.
  @param sweepId - The id of the sweep (-1 if no sweep).
  @param sweepElementId - The element in the sweep (-1 if no sweep).
  @return The specified result record.
  '''
  def GetResult(self, buildId, libaryId, datasetId, methodId, sweepId=-1,
                sweepElementId=-1):
    with self.con:
      if sweepId != -1:
        self.cur.execute("SELECT * FROM results WHERE build_id=" + str(buildId)
            + " AND libary_id=" + str(libaryId) + " AND dataset_id="
            + str(datasetId) + " AND method_id=" + str(methodId)
            + " AND sweep_id=" + str(sweepId) + " AND sweep_element_id="
            + str(sweepElementId))
      else:
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
  @param sweepId - The id of the sweep (-1 if no sweep).
  @param sweepElementId - The element of the sweep (-1 if no sweep).
  '''
  def UpdateResult(self, buildId, libaryId, time, var, datasetId, methodId,
                   sweepId=-1, sweepElementId=-1):
    with self.con:
      if self.GetResult(buildId, libaryId, datasetId, methodId, sweepId,
                        sweepElementId):
        if sweepId != -1:
          self.cur.execute("UPDATE results SET time=" + str(time) + ",var="
              + str(var) + " WHERE build_id=" + str(buildId) + " AND libary_id="
              + str(libaryId) + " AND dataset_id=" + str(datasetId)
              + " AND method_id=" + str(methodId) + " AND sweepId="
              + str(sweepId) + " AND sweepElementId=" + str(sweepElementId))
        else:
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
          "' AND parameters='" + json.dumps(parameters) + "'")
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
      command = "INSERT INTO methods VALUES (NULL,%s,%s,%s)"

      if self.driver == "mysql":
        self.cur.execute(command, (name, json.dumps(parameters), alias))
        self.cur.execute("SELECT LAST_INSERT_ID()")

      elif self.driver == "sqlite":
        self.cur.execute(command % ('?', '?', '?'), (name,
            json.dumps(parameters), alias))
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
        command = "INSERT INTO results VALUES (NULL,%s,%s,%s,%s,%s,%s)"

        if self.driver == "mysql":
          self.cur.execute(command,
              (newBuildId, res[2], res[3], res[4], res[5], res[6]))

        elif self.driver == "sqlite":
          self.cur.execute(command % ('?', '?', '?', '?', '?', '?'),
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
  @param sweepId - The id of the parameter sweep (-1 if no sweep).
  @param sweepElementId - The element of the sweep this record is for (-1 if no
      sweep).
  @param memoryInfo - The text for the memory value.
  '''
  def NewMemory(self, buildId, libaryId, methodId, datasetId, memoryInfo,
      sweepId=-1, sweepElementId=-1):
    with self.con:
      command = "INSERT INTO memory VALUES (NULL,%s,%s,%s,%s,%s,%s,%s)"

      if self.driver == "mysql":
        self.cur.execute(command,
            (buildId, libaryId, methodId, datasetId, sweepId, sweepElementId,
             memoryInfo))

      elif self.driver == "sqlite":
        self.cur.execute(command % ('?', '?', '?', '?', '?', '?', '?'),
            (buildId, libaryId, methodId, datasetId, sweepId, sweepElementId,
             memoryInfo))

  '''
  Update the given memory record in the memory table if the record is available
  otherwise create a new record.

  @param buildId - The build id.
  @param libaryId - The id of the library.
  @param methodId - The id of the method
  @param datasetId - The id of the dataset.
  @param sweepId - The id of the parameter sweep (-1 if no sweep).
  @param sweepElementId - The element of the sweep this record is for (-1 if no
      sweep).
  @param memoryInfo - The text for the memory value.
  '''
  def UpdateMemory(self, buildId, libaryId, methodId, datasetId, memoryInfo,
      sweepId=-1, sweepElementId=-1):
    with self.con:
      if sweepId != -1:
        if self.GetMemoryResults(buildId, libaryId, methodId, sweepId,
            sweepElementId):
          self.cur.execute("UPDATE memory SET memory_info=\'" + memoryInfo
            + "\' WHERE build_id=" + str(buildId) + " AND libary_id="
            + str(libaryId) + " AND dataset_id=" + str(datasetId)
            + " AND method_id=" + str(methodId) + " AND sweepId="
            + str(sweepId) + " AND sweepElementId=" + str(sweepElementId))
        else:
          self.NewMemory(buildId, libaryId, methodId, datasetId, memoryInfo,
              sweepId, sweepElementId)

      else:
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
  @param sweepId - The id of the sweep (-1 if no sweep).
  @param sweepElementId - The element of the sweep that is desired (-1 if no
      sweep).
  @return The memory informations of the method.
  '''
  def GetMemoryResults(self, buildId, libaryId, methodId, sweepId=-1,
      sweepElementId=-1):
    with self.con:
      if sweepId == -1:
        self.cur.execute("SELECT * FROM memory JOIN datasets ON " +
          "memory.dataset_id = datasets.id WHERE libary_id=" + str(libaryId) +
          " AND build_id="+ str(buildId) + " AND method_id=" + str(methodId))
      else:
        self.cur.execute("SELECT * FROM memory JOIN datasets ON " +
            "memory.dataset_id = datasets.id WHERE libary_id=" + str(libaryId) +
            " AND build_id=" + str(buildId) + " AND method_id=" +
            str(methodId) + " AND sweepId=" + str(sweepId) +
            " AND sweepElementId=" + str(sweepElementId))
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
      command = "INSERT INTO method_info VALUES (NULL,%s,%s)"

      if self.driver == "mysql":
        self.cur.execute(command, (methodId, info))

      elif self.driver == "sqlite":
        self.cur.execute(command % ('?', '?'), (methodId, info))

  '''
  Get the parameters of a given method.

  @param methodId - The id of the method.
  @return The parameters of the method.
  '''
  def GetMethodParameters(self, methodId):
    with self.con:
      self.cur.execute("SELECT parameters FROM methods WHERE id=" +
          str(methodId))
      return json.loads(self.cur.fetchall())

  '''
  Get the id of a given sweep.

  @param sweepType The string 'float' or 'int'.
  @param sweepBegin The starting point of the sweep.
  @param sweepStep The step size of the sweep.
  @param sweepEnd The ending point of the sweep.
  '''
  def GetSweep(self, sweepType, sweepBegin, sweepStep, sweepEnd):
    with self.con:
      self.cur.execute("SELECT id FROM sweeps WHERE type='"
          + sweepType + "' AND begin='" + str(sweepBegin)
          + "' AND step='" + str(sweepStep) + "' AND end='"
          + str(sweepEnd) + "'")
      return self.cur.fetchall()
