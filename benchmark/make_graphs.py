'''
  @file make_graphs.py
  @author Marcus Edel

  Functions to plot graphs.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains
# symlinks to modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], '../util')))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from graph import *
from log import *

'''
Parse the logfile and create the data structure.

@param logfile - Logfile that contains the results.
@return Data structure that contains all the data.
'''
def ParseLogFile(logfile):
  fid = open(logfile, "r")
  data = {}

  while 1:
    # Read the logfile line by line.
    line = fid.readline()
    if not line:
      break

    # Split the timestamp.
    line = line.split(" : ")
    timestamp = line[0]

    # Split the other values.
    line = line[1].split(":")

    libary = line[0]  # Libary name.
    method = line[1]  # Method name.
    options = line[2] # Method options.
    dataset = line[3] # Dataset name.
    time = line[4]    # measured time.
    var = line[5]     # Variance of the timing data.

    # Generate the big datastructure.
    if method in data:
      td = data[method]
      if options in td:
        tdn = td[options]
        if libary in tdn:
          tdn[libary].append((dataset, time, timestamp))
        else:
          tdn[libary] = [(dataset, time, timestamp)]
      else:
        t = {}
        t[libary] = [(dataset, time, timestamp)]
        td[options] = t
    else:
      d = {}
      t = {}      
      t[libary] = [(dataset, time, timestamp)]
      d[options] = t
      data[method] = d

  # Close the results file.
  fid.close()
  return data

'''
Create a bar chart with the given data.

@param data - Data structure form the logfile.
'''
def MakeBarCharts(data):
  # Write the data to a table.
  for methodName, sets in data.items():
    for option, libraries in sets.items():

      # Create the Table.
      table = []
      header = ['']
      table.append(header)

      # Count the datasets to get the correct table size.      
      datasetCount = CountLibrariesDatasets(libraries)

      # Create the matrix which contains the time and dataset informations.
      dataMatrix = [['-' for x in range(len(libraries) + 1)] 
          for x in range(datasetCount)] 

      col = 1
      for libaryName, datasets in sets[option].items():
        # Add the libary name to the header.
        header.append(libaryName)

        for dataset in datasets:
          # Unpack the attributes.
          name = dataset[0] # Dataset name.
          time = dataset[1] # Messaured time.

          # Find the correct position for the timing data in the table.
          row = FindRightRow(dataMatrix, name, datasetCount)  

          # Set the dataset name and the timing data.    
          dataMatrix[row][0] = name
          dataMatrix[row][col] = time
        col += 1

    # Show the table.
    Log.Notice("\n\n")
    Log.PrintTable(AddMatrixToTable(dataMatrix, table))
    Log.Notice("\n\n")

    # Generate the bar chart a save it.
    GenerateBarChart(header[1:], dataMatrix, methodName)

'''
Create a line chart with the given data.

@param data - Data structure form the logfile.
'''
def MakeMutliLineCharts(data):
  # Write the data to a table.
  for methodName, sets in data.items():
    for option, libraries in sets.items():
      dataSeries = {}
      col = 1
      for libaryName, datasets in sets[option].items():
        # Add the libary name to the header.

        timeSeries = {}

        for dataset in datasets:
          # Unpack the attributes.
          name = dataset[0]       # Dataset name.
          time = dataset[1]       # Messaured time.
          timestamp = dataset[2]  # The timestamp.

          # Concatenate the timing data for the dataset.
          if name in timeSeries:
            timeSeries[name].append((timestamp, time))
          else:
            timeSeries[name]= [(timestamp, time)]

        col += 1
        dataSeries[libaryName] = timeSeries
    
    # Generate the line chart a save it.
    GenerateLineChart(dataSeries, methodName)

if __name__ == '__main__':
  logfile = ParseLogFile("results.log")
  MakeBarCharts(logfile)
  