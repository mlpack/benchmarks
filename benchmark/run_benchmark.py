'''
  @file run_benchmark.py
  @author Marcus Edel

  Perform the timing benchmark.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains
# symlinks to modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], '../util')))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from log import *
from system import *
from loader import *
from parser import *
from convert import *
from misc import *
from database import *

import random
import argparse
import datetime
import simplejson

'''
Show system informations. Are there no data available, the value is 'N/A'.
'''
def SystemInformation():

  Log.Info("CPU Model: " + SystemInfo.GetCPUModel())
  Log.Info("Distribution: " + SystemInfo.GetDistribution())
  Log.Info("Platform: " + SystemInfo.GetPlatform())
  Log.Info("Memory: " + SystemInfo.GetMemory())
  Log.Info("CPU Cores: " + SystemInfo.GetCPUCores())

'''
Return a list with modified datasets.

@param dataset - Datasets to be modified.
@param format - List of file formats to be converted to.
@return List of modified datasets.
'''
def GetDataset(dataset, format):
  # Check if the given dataset is a list or a single dataset.
  if not isinstance(dataset, str):
    datasetList = []
    modifiedList = []

    for data in dataset:
      mdata = CheckFileExtension(data, format)

      # Check if the dataset is available.
      if os.path.isfile(mdata):
        datasetList.append(mdata)
      else:
        # Convert the dataset in the given format.
        convert = Convert(data, format[0])
        datasetList.append(convert.modifiedDataset)
        modifiedList.append(convert.modifiedDataset)
  else:
    datasetList = ""
    modifiedList = ""

    mdataset = CheckFileExtension(dataset, format)

    # Check if the dataset is available.
    if os.path.isfile(mdataset):
      datasetList = mdataset
    else:
      # Convert the dataset in the given format.
      convert = Convert(dataset, format[0])
      datasetList = convert.modifiedDataset
      modifiedList = convert.modifiedDataset

  return (datasetList, modifiedList)

'''
Count all datasets to determine the dataset number of datasets.

@param libraries - Contains the dataset list.
@return Dataset count.
'''
def CountLibrariesDatasets(libraries):
  datasetList = []
  for library in libraries:
    for dataset in library[1]:
      name = NormalizeDatasetName(dataset)
      if not name in datasetList:
        datasetList.append(name)

  return len(datasetList)

'''
Start the main benchmark routine. The method shows some DEBUG information and
prints a runtime information table.

@param configfile - Start the benchmark with the given configuration file.
@param blocks - Run only the specified blocks.
@param log - If True save the reports otherwise use stdout and print the reports.
@param methodBlocks - Run only the specified methods.
@param update - Update the records in the database.
'''
def Main(configfile, blocks, log, methodBlocks, update):
  # Benchmark settings.
  timeout = 23000
  database = "reports/benchmark.db"

  bootstrapCount = 10

  # Create the folder structure.
  CreateDirectoryStructure(["reports/img", "reports/etc"])

  #Create the bootstrapped method dictionary which will contain the
  #normalized values of all metrics for all methods
  bootstrapped_method_dict = {}

  # Read the config.
  config = Parser(configfile, verbose=False)
  streamData = config.StreamMerge()

  # Read the general block and set the attributes.
  if "general" in streamData:
    for key, value in streamData["general"]:
      if key == "timeout":
        timeout = value
      if key == "database":
        database = value
      if key == "bootstrap":
        bootstrapCount = value

  # Create database connection if the user asked for to save the reports.
  if log:
    db = Database(database)
    db.CreateTables()

  # Transform the blocks string to a list.
  if blocks:
    blocks = blocks.split(",")

  # Temporary datastructures for the current build.
  build = {}

  # Iterate through all libraries.
  for method, sets in streamData.items():
    if method == "general":
      continue
    if not methodBlocks or method in methodBlocks:
      Log.Info("Method: " + method)
      for options, libraries in sets.items():
        Log.Info("Options: " + (options if options != "" else "None"))

        if log:
          methodId = db.GetMethod(method, options)
          methodId = methodId[0][0] if methodId else db.NewMethod(method,
                                                                  options,
                                                                  "None")

        # Create the result table.
        table = []
        header = ['']
        table.append(header)

        # Count the datasets.
        datasetCount = CountLibrariesDatasets(libraries)

        # Create the matrix which contains the time and dataset informations.
        dataMatrix = [['-' for x in range(len(libraries) + 1)] for x in
            range(datasetCount)]

        #Dictionary which will contain key as the library name and value as
        #a dictionary of metrics for the current method
        method_dict = {}

        col = 1
        run = 0
        for library in libraries:
          name = library[0]
          datasets = library[1]
          trials = library[2]
          script = library[3]
          format = library[4]
          tasks = library[5]
          alias = library[6]

          if log:
            db.UpdateMethod(methodId, alias)

          header.append(name)

          if not blocks or name in blocks:
            run += 1
            Log.Info("Library: " + name)

            # Logging: create a new build and library record for this library.
            if log and name not in build:
              libraryId = db.GetLibrary(name)
              libraryId = libraryId[0][0] if libraryId else db.NewLibrary(name)

              if update:
                buildId = db.GetLatestBuildFromLibary(libraryId)
                if buildId >= 0:
                  build[name] = (buildId, libraryId)
                else:
                  Log.Warn("Nothing to update.")
                  continue
              else:
                build[name] = (db.NewBuild(libraryId), libraryId)

            # Load the script.
            try:
              module = Loader.ImportModuleFromPath(script)
              methodCall = getattr(module, method)
            except Exception as e:
              Log.Fatal("Could not load the script: " + script)
              Log.Fatal("Exception: " + str(e))
            else:

              for dataset in datasets:
                datasetName = NormalizeDatasetName(dataset)
                row = FindRightRow(dataMatrix, datasetName, datasetCount)

                # Logging: Create a new dataset record fot this dataset.
                if log:
                  datasetId = db.GetDataset(datasetName)
                  datasetId = datasetId[0][0] if datasetId else db.NewDataset(*DatasetInfo(dataset))

                dataMatrix[row][0] = datasetName
                Log.Info("Dataset: " + dataMatrix[row][0])

                modifiedDataset = GetDataset(dataset, format)

                try:
                  instance = methodCall(modifiedDataset[0], timeout=timeout,
                    verbose=False)
                except Exception as e:
                  Log.Fatal("Could not call the constructor: " + script)
                  Log.Fatal("Exception: " + str(e))
                  continue

                # Logging: Add method information record.
                if log:
                  try:
                    # Some script define a method description, if
                    # the description is set, save this in the database.
                    methodDescription = instance.description
                  except AttributeError:
                    pass
                  else:
                    # Only store the description in the databse if there isn't
                    # a description.
                    if methodDescription and not db.GetMethodInfo(methodId):
                      db.NewMethodInfo(methodId, methodDescription)

                if 'timing' in tasks:
                  time = []
                  for trial in range(trials + 1):
                    if trial > 0:
                      try:
                        time.append(instance.RunTiming(options))

                        # Method unsuccessful.
                        if sum(time) < 0:
                          break
                      except Exception as e:
                        Log.Fatal("Exception: " + str(e))

                  # Set the correct time label.
                  if sum(time) == -2:
                    # Timout failure.
                    dataMatrix[row][col] = ">" + str(timeout)
                  elif sum(time) < 0:
                    # Exception.
                    dataMatrix[row][col] = "failure"
                  else:
                    # Measured time.
                    dataMatrix[row][col] = "{0:.6f}".format(sum(time) / trials)

                  # Save the results in the databse if the user asked for.
                  if log:
                    # Get the variance.
                    var = 0
                    if len(time) != 0:
                      avg = sum(time) / len(time)
                      var = sum((avg - value) ** 2 for value in time) / len(time)

                    buildId, libraryId = build[name]
                    if update:
                      try:
                        db.UpdateResult(buildId, libraryId, dataMatrix[row][col],
                          var, datasetId, methodId)
                      except Exception:
                        pass
                    else:
                      db.NewResult(buildId, libraryId, dataMatrix[row][col], var,
                          datasetId, methodId)


                if 'metric' in tasks:
                  try:
                    metrics = instance.RunMetrics(options)
                  except Exception as e:
                    Log.Fatal("Exception: " + str(e))
                    metrics = None

                  if metrics:
                    if log:
                      buildID, libraryID = build[name]
                      if update:
                        try:
                          db.UpdateMetricResult(buildID, libraryID,
                              simplejson.dumps(metrics), datasetId, methodId)
                        except Exception:
                          pass
                      else:
                        db.NewMetricResult(buildID, libraryID,
                            simplejson.dumps(metrics), datasetId, methodId)

                if 'bootstrap' in tasks:
                  bootstrap_metrics = {}

                  # Start bootstrapping for this method.
                  bootstrapCounter = 0
                  for i in range(bootstrapCount):
                    instance = methodCall(modifiedDataset[0], timeout=timeout,
                        verbose=False)

                    # Get the metric results for the specified method.
                    metrics = instance.RunMetrics(options)

                    # Merge the obtained metrics with the existing.
                    if metrics:
                      bootstrapCounter += 1
                      bootstrap_metrics = { m: metrics.get(m, 0) +
                                            bootstrap_metrics.get(m, 0)
                                            for m in set(metrics) }

                  # Normalize each obtained metric.
                  for m in bootstrap_metrics:
                    bootstrap_metrics[m] = float("{0:.6f}".format
                                                 (round(bootstrap_metrics[m] /
                                                  bootstrapCounter, 5)))

                  # Store the results in db if the user asked for it.
                  if log:
                    buildID, libraryID = build[name]
                    if update:
                      try:
                        db.UpdateBootstrapResult(buildID, libraryID,
                            simplejson.dumps(bootstrap_metrics), datasetId,
                            methodId)
                      except Exception as e:
                        pass
                    else:
                      db.NewBootstrapResult(buildID, libraryID,
                          simplejson.dumps(bootstrap_metrics), datasetId,
                          methodId)

                # Remove temporary datasets.
                RemoveDataset(modifiedDataset[1])
          col += 1
        # Show the results.
        if not log and run > 0 and 'timing' in tasks:
          Log.Notice("\n\n")
          Log.PrintTable(AddMatrixToTable(dataMatrix, table))
          Log.Notice("\n\n")
          run = 0

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="""Perform the benchmark with the
      given config.""")
  parser.add_argument('-c','--config', help='Configuration file name.',
      required=True)
  parser.add_argument('-b','--blocks', help='Run only the specified blocks.',
      required=False)
  parser.add_argument('-l','--log', help='Save the results in the logfile.',
      required=False)
  parser.add_argument('-u','--update', help="""Update the results in the
      database.""", required=False)
  parser.add_argument('-m','--methodBlocks', help="""Run only the specified
      method blocks.""", required=False)

  args = parser.parse_args()

  if args:
    SystemInformation()
    log = True if args.log == "True" else False
    update = True if args.update == "True" else False
    Main(args.config, args.blocks, log, args.methodBlocks, update)
