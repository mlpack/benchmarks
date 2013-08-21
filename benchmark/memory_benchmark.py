'''
  @file memory_benchmark.py
  @author Marcus Edel

  Perform the memory benchmark.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains
# symlinks to modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], '../util')))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from log import *
from loader import * 
from parser import *
from convert import *
from misc import *
from database import *

import argparse
import datetime


'''
Return a list with modified dataset.

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
        # Check if the dataset is available.
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
      # Convert the Dataset.
      convert = Convert(dataset, format[0])
      datasetList = convert.modifiedDataset
      modifiedList = convert.modifiedDataset

  return (datasetList, modifiedList)

def Main(configfile, blocks, log):
  # Benchmark settings.
  timeout = 23000
  database = "reports/benchmark.db"

  # Create the folder structure.
  CreateDirectoryStructure(["reports/img", "reports/etc"])

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

  # Temporary datastructures for the current build.
  build = {}

  # Open logfile if the user asked for.
  if log:
    db = Database(database)
    db.CreateTables()

  # Transform the blocks string to a list.
  if blocks:
    blocks = blocks.split(",")

  # Iterate through all libraries.
  for method, sets in streamData.items():
    if method == "general":
      continue
    Log.Info("Method: " + method)    
    for options, libraries in sets.items():
      Log.Info('Options: ' + (options if options != '' else 'None'))

      if log:
        methodId = db.GetMethod(method, options)
        methodId = methodId[0][0] if methodId else db.NewMethod(method, options)

      for libary in libraries:
        name = libary[0]
        datsets = libary[1]
        script = libary[3]
        format = libary[4]
        
        if not blocks or name in blocks:
          Log.Info("Libary: " + name)

          # Logging: create a new library record for this library.
          if log and name not in build:
            libaryId = db.GetLibrary(name + "_memory")
            libaryId = libaryId[0][0] if libaryId else db.NewLibrary(name + "_memory")

            build[name] = (db.NewBuild(libaryId), libaryId)

          # Load the script.
          try:
            module = Loader.ImportModuleFromPath(script)
            methodCall = getattr(module, method)
          except Exception as e:
            Log.Fatal("Could not load the script: " + script)
            Log.Fatal("Exception: " + str(e))
          else:

            for dataset in datsets:
              datasetName = NormalizeDatasetName(dataset)

              # Logging: Create a new dataset record fot this dataset.
              if log:
                datasetId = db.GetDataset(datasetName)
                datasetId = datasetId[0][0] if datasetId else db.NewDataset(*DatasetInfo(dataset))

              Log.Info("Dataset: " + datasetName)
              modifiedDataset = GetDataset(dataset, format)

              try:
                instance = methodCall(modifiedDataset[0], timeout=timeout, 
                  verbose=False)
              except Exception as e:
                Log.Fatal("Could not call the constructor: " + script)
                Log.Fatal("Exception: " + str(e))
                continue

              # Generate a "unique" name for the memory output file.
              outputName = "reports/etc/" + str(hash(datetime.datetime.now())) + ".mout"

              try:
                err = instance.RunMemoryProfiling(options, outputName);
              except Exception as e:
                Log.Fatal("Exception: " + str(e))
                
                # Remove temporary datasets.
                RemoveDataset(modifiedDataset[1])
                continue

              # Save results in the database if the user asked for.
              if err != -1 and log:
                buildId, libaryId = build[name]
                db.NewMemory(buildId, libaryId, methodId, datasetId, outputName)

              # Remove temporary datasets.
              RemoveDataset(modifiedDataset[1])

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="""Perform the benchmark with the
      given config.""")
  parser.add_argument('-c','--config', help='Configuration file name.', 
      required=True)
  parser.add_argument('-b','--blocks', help='Run only the specified blocks.', 
      required=False)
  parser.add_argument('-l','--log', help='Save the results in the logfile.', 
      required=False)

  args = parser.parse_args()

  if args:
    log = True if args.log == "True" else False
    Main(args.config, args.blocks, log)
