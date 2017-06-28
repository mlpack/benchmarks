'''
  @file run_benchmark.py
  @author Marcus Edel

  Perform the timing benchmark.
'''

import os, sys, inspect, json
import math
from copy import copy

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

try:
  from irc_bot import *
  irc_available = True
except ImportError:
  irc_available = False

import random
import argparse
import datetime

try:
  import simplejson
except ImportError:
  Log.Warn("No module named simplejson")

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

    if "." in dataset:
      mdataset = CheckFileExtension(dataset, format)

      # Check if the dataset is available.
      if os.path.isfile(mdataset):
        datasetList = mdataset
      else:
        # Convert the dataset in the given format.
        convert = Convert(dataset, format[0])
        datasetList = convert.modifiedDataset
        modifiedList = convert.modifiedDataset
    else:
      datasetList = dataset

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
def Main(configfile, blocks, log, methodBlocks, update, watchFiles, new,
    databaseUser, databasePassword):
  # Benchmark settings.
  timeout = 23000
  database = "reports/benchmark.db"
  driver = "sqlite"
  databaseHost = None
  databasePort = 3306

  bootstrapCount = 10

  watchFiles = watchFiles.split()

  # Create the folder structure.
  CreateDirectoryStructure(["reports/img", "reports/etc"])

  #Create the bootstrapped method dictionary which will contain the
  #normalized values of all metrics for all methods
  bootstrapped_method_dict = {}

  # Read the config.
  config = Parser(configfile, verbose=False)
  streamData = config.StreamMerge()
  ircData = None

  # Summary parameter.
  summaryBenchmarks = 0
  summaryDifference = 0
  differenceThreshold = 10

  # Read the general block and set the attributes.
  if "general" in streamData:
    for key, value in streamData["general"]:
      if key == "timeout":
        timeout = value
      if key == "database":
        database = value
      if key == "bootstrap":
        bootstrapCount = value
      if key == "irc":
        ircData = value
      if key == "driver":
        driver = value
      if key == "databaseHost":
        databaseHost = value
      if key == "databaseUser":
        databaseUser = value
      if key == "databasePassword":
        databasePassword = value
      if key == "port":
        databasePort = value

  # Create database connection if the user asked for to save the reports.
  if log:
    db = Database(driver=driver, database=database, host=databaseHost,
        user=databaseUser, password=databasePassword, port=databasePort)
    db.CreateTables()

  if irc_available and ircData:
    ircBOT = IRCBot(ircData[0], ircData[1], ircData[2])
    watchMessages = []

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
        # Remove newlines tabs and whitespace on the left and right side from
        # the options parameter string.
        if options == '':
          options = {}
        else:
          options = json.loads(options)

        Log.Info("Options: " + (str(options) if options != {} else "None"))

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

        # Create the matrix which contains the time from the previous run.
        dataMatrixPrevious = [['-' for x in range(len(libraries) + 1)] for x in
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
          files = library[7]

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
                if new:
                  buildId = db.GetLatestBuildFromLibary(libraryId)[0][0]
                  if buildId:
                    newBuildId = db.NewBuild(libraryId)
                    db.CopyLatestBuildFromLibary(buildId, newBuildId)

                buildId = db.GetLatestBuildFromLibary(libraryId)

                # Get the right build id from the list.
                if buildId and type(buildId) is list:
                  if(type(buildId[0]) is tuple):
                    buildId = buildId[0][0]
                  else:
                    buildId = buildId[0]

                buildIdPrevious = [(buildId,)]

                if buildId:
                  build[name] = (buildId, libraryId)
                else:
                  Log.Warn("Nothing to update.")
                  continue
              else:
                if db.GetLatestBuildFromLibary(libraryId)[0][0] <= 0:
                  buildIdPrevious = [(1,)]
                else:
                  buildIdPrevious = db.GetLatestBuildFromLibary(libraryId)

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
                dataMatrixPrevious[row][0] = datasetName

                Log.Info("Dataset: " + dataMatrix[row][0])

                modifiedDataset = GetDataset(dataset, format)

                # Do we need to do any sweeps?
                sweep = ["sweep" in str(v) for k, v in
                    options.items()].count(True) > 0
                if sweep:
                  # Parse the sweep.
                  for k, v in options.items():
                    if "sweep" in str(v):
                      p = re.compile(r"sweep\([ \t]*(?P<begin>[-0-9.e]*),[ \t]*"
                          "(?P<step>[-0-9.e]*)[ \t]*,[ \t]*"
                          "(?P<end>[-0-9.e]*)[ \t]*\)")
                      m = p.match(str(v))
                      sweep_begin = m.group("begin")
                      sweep_step = m.group("step")
                      sweep_end = m.group("end")
                      sweep_name = k
                      # Get the type of the sweep.
                      def sweepType(sweep_begin, sweep_step, sweep_end):
                        try:
                          a = int(sweep_begin)
                          b = int(sweep_step)
                          c = int(sweep_end)
                          return 'int'
                        except ValueError:
                          try:
                            a = float(sweep_begin)
                            b = float(sweep_step)
                            c = float(sweep_end)
                            return 'float'
                          except ValueError:
                            Log.Fatal("cannot parse sweep: " + str(v))
                            raise Exception("cannot parse sweep")

                      sweep_type = sweepType(sweep_begin, sweep_step, sweep_end)
                      break

                  sweep_len = math.ceil((float(sweep_end) - float(sweep_begin)) /
                      float(sweep_step)) + 1
                  # Get a sweep id.
                  if log:
                    sweep_id = db.GetSweep(sweep_type, sweep_begin, sweep_step,
                        sweep_end)
                    sweep_id = sweep_id[0][0] if sweep_id else \
                        db.NewSweep(sweep_type, sweep_begin, sweep_step, sweep_end)
                else:
                  sweep_len = 1
                  if log:
                    sweep_id = -1

                for sweep_elem in range(sweep_len):
                  # Generate the options.
                  run_options = copy(options)
                  if sweep:
                    # Modify option value.
                    def to_num(s):
                      try:
                        return int(s)
                      except ValueError:
                        return float(s)

                    run_options[sweep_name] = to_num(sweep_begin) + \
                        to_num(sweep_step) * sweep_elem
                    Log.Info("- Sweep step " + str(sweep_elem + 1) + " of "
                        + str(sweep_len) + " (" + sweep_name + ": "
                        + str(run_options[sweep_name]) + ")")

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

                  if 'watch' in tasks and log:
                    watchCheck = False
                    checkFiles = [method, method.lower()] + files

                    for checkFile in checkFiles:
                      for watchFile in watchFiles:
                        if checkFile in watchFile:
                          watchCheck = True
                          break;

                    if not watchCheck:
                      continue

                  if 'metric' in tasks:
                    metrics = []

                    for trial in range(trials):
                      try:
                        currentMetric = instance.RunMetrics(run_options)

                        if type(currentMetric) is not dict and currentMetric == -2:
                          # Timout failure.
                          metrics = [{ 'Runtime' :  ">" + str(timeout)}]
                          break
                        elif type(currentMetric) is not dict and currentMetric < 0:
                          # Runtime exception.
                          metrics = [{ 'Runtime' :  "failure"}]
                          break
                        else:
                          # Append new data.
                          metrics.append(currentMetric)
                      except Exception as e:
                        Log.Fatal("Exception: " + str(e))
                        raise e

                    finalMetrics = {}
                    if len(metrics) > 0:
                      finalMetrics = metrics[0]
                      for m in range(1, len(metrics)):
                        for metricKey in metrics[m]:
                          value = metrics[m][metricKey]

                          if isFloat(value) or isInt(value):
                            finalMetrics[metricKey] += value

                    for metricKey in finalMetrics:
                      value = finalMetrics[metricKey]
                      if isFloat(value) or isInt(value):
                        finalMetrics[metricKey] /= len(metrics)

                        # Convert to int if possible.
                        if (finalMetrics[metricKey] == int(finalMetrics[metricKey])):
                          finalMetrics[metricKey] = int(finalMetrics[metricKey])

                    # Update the Runtime matrix view.
                    if 'Runtime' in finalMetrics:
                      if ">" in str(finalMetrics['Runtime']):
                        # Runtime timeout.
                        dataMatrix[row][col] = -1
                      elif "failure" == str(finalMetrics['Runtime']):
                        # Runtime failure.
                        dataMatrix[row][col] = -2
                      elif isFloat(finalMetrics['Runtime']):
                        # Truncate to specified precision.
                        if sweep_elem == 0:
                          dataMatrix[row][col] = "{0:.6f}".format(finalMetrics['Runtime'])
                        elif sweep_elem == sweep_len - 1:
                          dataMatrix[row][col] = dataMatrix[row][col] + \
                              "-{0:.6f}".format(finalMetrics['Runtime'])
                      else:
                        # Integer, no need to specify the precision.
                        if sweep_elem == 0:
                          dataMatrix[row][col] = str(finalMetrics['Runtime'])
                        elif sweep_elem == sweep_len - 1:
                          dataMatrix[row][col] = dataMatrix[row][col] + "-" + \
                              str(finalMetrics['Runtime'])

                    if log:
                      buildID, libraryID = build[name]

                      if update:
                        try:
                          # Update metric data.
                          db.UpdateMetricResult(buildID, libraryID,
                              simplejson.dumps(finalMetrics), datasetId,
                              methodId, sweep_id, sweep_elem)

                          # Update runtime data.
                          db.UpdateResult(buildID, libraryID,
                              finalMetrics['Runtime'], 0, datasetId, methodId,
                              sweep_id, sweep_elem)
                        except Exception:
                          pass
                      else:
                        # Add new metric results.
                        db.NewMetricResult(buildID, libraryID,
                            simplejson.dumps(finalMetrics), datasetId, methodId,
                            sweep_id, sweep_elem)

                        # Add new runtime results.
                        db.NewResult(buildID, libraryID, finalMetrics['Runtime'],
                            0, datasetId, methodId, sweep_id, sweep_elem)

                    if 'watch' in tasks and log:
                      for prevbuildID in buildIdPrevious:
                        resultsPrevious = db.GetResult(prevbuildID[0], libraryID,
                            datasetId, methodId, sweep_id, sweep_elem)
                        if (resultsPrevious and resultsPrevious[0][3] != '-'):
                          break

                      if resultsPrevious:
                        dataMatrixPrevious[row][col] = str(resultsPrevious[0][3])

                # Remove temporary datasets.
                RemoveDataset(modifiedDataset[1])
          col += 1
        # Show the results.
        if not log and run > 0:
          Log.Notice("\n\n")
          Log.PrintTable(AddMatrixToTable(dataMatrix, table))
          Log.Notice("\n\n")
          run = 0

        if 'watch' in tasks and log:
          Log.Notice("\n\n")
          Log.PrintTable(AddMatrixToTable(dataMatrix, table))

          resultsMessage = method
          if options:
            resultsMessage += " (" + options + ")"

          resultsMessage += " | "
          for result in zip(dataMatrixPrevious, dataMatrix):
            if result[0][1] != '-' and result[1][1] != '-':

              # Increase the number of benchmark results for the summary.
              summaryBenchmarks += 1

              # Truncate to specified precision.
              if isFloat(result[0][1]):
                timeOld = "{0:.2f}".format(float(result[0][1]))
              else:
                timeOld = result[0][1]

              if isFloat(result[1][1]):
                timeCurrent = "{0:.2f}".format(float(result[1][1]))
              else:
                timeCurrent = result[1][1]

              if isFloat(result[0][1]) and isFloat(result[1][1]):
                new = float(result[1][1])
                old = float(result[0][1])

                timeDiffValue = new - old
                timeDiff = "{0:.2f}".format(timeDiffValue)

                if (new - old) > 0:
                  offset = (differenceThreshold * old) / 100
                  if timeDiffValue > 0 and timeDiffValue > offset:
                    summaryDifference += 1

              else:
                timeDiff = "-"

              # Add dataset name.
              resultsMessage += result[0][0] + " "
              # Add old runtime.
              resultsMessage += timeOld + " (old) => "
              # Add current runtime.
              resultsMessage += timeCurrent + " (new) => "
              # Add runtime difference.
              resultsMessage += timeDiff + " (diff) | "

          if "=>" in resultsMessage:
            if irc_available and ircData:
              watchMessages.append(resultsMessage)
            else:
              Log.Info(resultsMessage)

          Log.Notice("\n\n")

  if irc_available and ircData and len(watchMessages) > 0:
    # Add summary message ("Benchmarks x of y passed").
    summaryMessage = "Benchmarks " + str(summaryBenchmarks - summaryDifference)
    summaryMessage += " of " + str(summaryBenchmarks) + " passed."
    watchMessages.append(summaryMessage)

    ircBOT.send_messages(watchMessages)


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
  parser.add_argument('-f','--files', help="""Run only blocks for the
      specified files.""", required=False)
  parser.add_argument('-n','--new', help="""Copy the database before
      performing the benchmark.""", required=False)
  parser.add_argument('-r','--user', help="""Database username.""",
      required=False)
  parser.add_argument('-p','--password', help="""Database password.""",
      required=False)

  args = parser.parse_args()

  if args:
    SystemInformation()
    log = True if args.log == "True" else False
    update = True if args.update == "True" else False
    args.files = "" if args.files == None else args.files
    new = True if args.new == "True" else False

    Main(args.config, args.blocks, log, args.methodBlocks, update, args.files,
        new, args.user, args.password)
