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

import argparse

'''
Show system informations. Are there no data available, the value is 'N/A'.
'''
def SystemInformation():
  
  Log.Info('CPU Model: ' + SystemInfo.GetCPUModel())
  Log.Info('Distribution: ' + SystemInfo.GetDistribution())
  Log.Info('Platform: ' + SystemInfo.GetPlatform())
  Log.Info('Memory: ' + SystemInfo.GetMemory())
  Log.Info('CPU Cores: ' + SystemInfo.GetCPUCores())

'''
Normalize the dataset name. If the dataset is a list of datasets, take the first
dataset as name. If necessary remove characters like '.', '_'.
'''
def NormalizeDatasetName(dataset):
  if  not isinstance(dataset, basestring):
    return os.path.splitext(os.path.basename(dataset[0]))[0]  
  else:
    return os.path.splitext(os.path.basename(dataset))[0]

def AddMatrixToTable(matrix, table):
  for row in matrix:
    table.append(row)
  return table

'''
Start the main benchmark routine. The method shows some DEBUG information and 
prints a table with the runtime information.
'''
def Main(configfile): 

  # Read Config.
  config = Parser(configfile, verbose=False)
  streamData = config.StreamMerge()

  # Iterate through all libraries.
  for method, sets in streamData.items():
    Log.Info("Method: " + method)    
    for options, libraries in sets.items():
      Log.Info('Options: ' + (options if options != '' else 'None'))

      # Create the Table.
      table = []
      header = ['']
      table.append(header)

      # Count the Datasets.
      datasetCount = 0
      for libary in libraries:
        datasetCount = max(datasetCount, len(libary[1]))

      # Create the matrix which contains the time and dataset informations.
      dataMatrix = [['-' for x in xrange(len(libraries) + 1)] for x in 
          xrange(datasetCount)] 

      col = 1
      for libary in libraries:
        name = libary[0]
        datsets = libary[1]
        trials = libary[2]
        script = libary[3]

        Log.Info("Libary: " + name)
        header.append(name)

        # Load script.
        module = Loader.ImportModuleFromPath(script)
        methodCall = getattr(module, method)       

        row = 0
        for dataset in datsets:          
          dataMatrix[row][0] = NormalizeDatasetName(dataset)
          Log.Info("Dataset: " + dataMatrix[row][0])        

          time = 0
          for trial in range(trials + 1):
            instance = methodCall(dataset, verbose=False)
            if trial > 0:
              time += instance.RunMethod(options);

          # Set time.
          dataMatrix[row][col] = "{0:.6f}".format(time / trials)
          row += 1
        col += 1

      # Show results in a table.
      Log.Notice("\n\n")
      Log.PrintTable(AddMatrixToTable(dataMatrix, table))
      Log.Notice("\n\n")

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="""Perform the benchmark with the
      given config.""")
  parser.add_argument('-c','--config', help='Configuration file name.', 
      required=True)

  args = parser.parse_args()

  if args:
    SystemInformation()
    Main(args.config)