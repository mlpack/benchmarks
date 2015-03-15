'''
  @file graph.py
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

from misc import *
from log import *
from template import *

import re, collections, simplejson, datetime

'''
Generate a bar chart for the metrics with the specified informations.

@param results - Contains the values to plot.
@param libraries - A list that contains the names of the libraries.
@param fileName - The filename of the line chart.
@param bestlib - The name of the library which should be compared with the other
libraries.
@return The dataset count, total time, failure count, timeout count,
best libray count, timing data.
'''
def GenerateBarChartMetric(results,libraries, fileName, datasetName, bestlib="mlpack"):
  # use this variable to count the time.
  totalTime = 0
  # Use this variable to count the timeouts.
  timeouts = 0
  # Use this variable to count the failures.
  failure = 0

  # Use this data structures to generate the timing table and the progress bar.
  timingData = {}

  # Use this variable to get use the data for the right library.
  l = 0

  # Iterate through the data and plot the bar chart.
  for result in results:
    for i, data in enumerate(result):
      if data[7] == datasetName:
        for key, value in simplejson.loads(data[3]).items():

          # The time value.
          time = value

          # The name of the dataset.
          dataset = key

          # Save the timing data for the timing table.
          if dataset in timingData:
            timingData[dataset][l] = time
          else:
            timingData[dataset] = ['-' for x in range(len(libraries))]
            timingData[dataset][l] = time

          # We can only plot scalar values so we jump over the other.
          if time == "failure":
            failure += 1
            continue
          elif str(time).count(">") > 0:
            timeouts += 1
            continue

          totalTime += time
    l += 1

  timingData = collections.OrderedDict(sorted(timingData.items()))

  tmp = timingData.copy()
  if failure > 0 or timeouts > 0:
    # Get the maximum value of the results.
    values = [item for sublist in timingData.values() for item in sublist]
    maxValue = [v if isFloat(v) else 1 for v in values]
    maxValue = max(maxValue)
  else:
    maxValue = 0

  build = str(abs(hash(datetime.datetime.now())))

  fileName = 'graphs/metric_' + str(build)

  header = 'dummy,'
  for dataset, timings in timingData.items():
    header += dataset + ','
  header = header[:-1] + '\n'

  # Write the csv file that contains the data.
  with open('reports/' + fileName + '.csv', 'wb+') as fid:
    # Write header line to file.
    fid.write(header.encode('UTF-8'))

    for i in range(len(libraries)):
      c = libraries[i] + ','
      for dataset, timings in timingData.items():
        if timings[i] == 'failure' or '>' in str(timings[i]) or '-' == timings[i]:
          c += '0,'
        else:
          c += str(timings[i]) + ','

      c = c[:-1]
      if i < len(libraries) - 1:
        c += '\n'
      fid.write(c.encode('UTF-8'))

  content = {}
  content['container'] = build
  content['type'] = 'column'
  content['title'] = datasetName
  content['subtitle'] = 'Hide data series by clicking the legend item.'
  content['xAxisLabels'] = 'true'
  content['xAxisRotation'] = '0' if len(header) < 130 else '-45'
  content['yAxis'] = 'Time [s]'
  content['tooltipText'] = 's'
  content['data'] = fileName + '.csv'

  with open('reports/' + fileName + '.js', 'wb+') as fid:
      c = chartTemplate % content
      fid.write(c.encode('UTF-8'))

  return (len(timingData), totalTime, failure, timeouts, 0, timingData, fileName + '.js', build)

'''
Generate a bar chart with the specified informations.

@param results - Contains the values to plot.
@param libraries - A list that contains the names of the libraries.
@param fileName - The filename of the line chart.
@param bestlib - The name of the library which should be compared with the other
libraries.
@return The dataset count, total time, failure count, timeout count,
best libray count, timing data.
'''
def GenerateBarChart(results, libraries, fileName, bestlib="mlpack"):
  # use this variable to count the time.
  totalTime = 0
  # Use this variable to count the timeouts.
  timeouts = 0
  # Use this variable to count the failures.
  failure = 0

  # Use this data structures to generate the timing table and the progress bar.
  timingData = {}

  # Use this variable to get use the data for the right library.
  l = 0
  # Iterate through the data and plot the bar chart.
  for result in results:
    for i, data in enumerate(result):
      # The time value.
      time = data[3]
      # The name of the dataset.
      dataset = data[8]

      # Save the timing data for the timing table.
      if dataset in timingData:
        timingData[dataset][l] = time
      else:
        timingData[dataset] = ['-' for x in range(len(libraries))]
        timingData[dataset][l] = time

      # We can only plot scalar values so we jump over the other.
      if time == "failure":
        failure += 1
        continue
      elif str(time).count(">") > 0:
        timeouts += 1
        continue

      totalTime += time
    l += 1

  timingData = collections.OrderedDict(sorted(timingData.items()))

  tmp = timingData.copy()
  if failure > 0 or timeouts > 0:
    # Get the maximum value of the results.
    values = [item for sublist in timingData.values() for item in sublist]
    maxValue = [v if isFloat(v) else 1 for v in values]
    maxValue = max(maxValue)
  else:
    maxValue = 0


  build = str(abs(hash(datetime.datetime.now())))

  fileName = 'graphs/timing_' + str(build)

  header = 'dummy,'
  for dataset, timings in timingData.items():
    header += dataset + ','
  header = header[:-1] + '\n'

  # Write the csv file that contains the data.
  with open('reports/' + fileName + '.csv', 'wb+') as fid:
    # Write header line to file.
    fid.write(header.encode('UTF-8'))

    for i in range(len(libraries)):
      c = libraries[i] + ','
      for dataset, timings in timingData.items():
        if timings[i] == 'failure' or ('>' in str(timings[i])) or '-' == timings[i]:
          c += '0,'
        else:
          c += str(timings[i]) + ','

      c = c[:-1]
      if i < len(libraries) - 1:
        c += '\n'
      fid.write(c.encode('UTF-8'))

  content = {}
  content['container'] = build
  content['type'] = 'column'
  content['title'] = ''
  content['subtitle'] = 'Hide data series by clicking the legend item.'
  content['xAxisLabels'] = 'true'
  content['xAxisRotation'] = '0' if len(header) < 130 else '-45'
  content['yAxis'] = 'Time [s]'
  content['tooltipText'] = 's'
  content['data'] = fileName + '.csv'

  with open('reports/' + fileName + '.js', 'wb+') as fid:
      c = chartTemplate % content
      fid.write(c.encode('UTF-8'))

  # Count the time in which bestlib is the best.
  bestLibCount = 0
  try:
    bestLibIndex = libraries.index(bestlib)
  except ValueError:
    pass
  else:
    for dataset, results in timingData.items():
      results = [v if isFloat(v) else float('Inf') for v in results]
      if bestLibIndex == results.index(min(results)):
        bestLibCount += 1

  return (len(timingData), totalTime, failure, timeouts, bestLibCount, timingData, fileName + '.js', build)

'''
Generate a memory chart with the specified informations.

@param massiflogFile - The massif logfile.
'''
def CreateMassifChart(massiflogFile, datasetName):
  # Read the massif logfile.
  try:
    with open(massiflogFile, "r") as fid:
      content = fid.read()
  except IOError as e:
    Log.Fatal("Exception: " + str(e))
    return

  # Parse the massif logfile.
  memHeapB = [(int(i) / 1024) + 0.0001 for i in re.findall(r"mem_heap_B=(\d*)", content)]
  memHeapExtraB = [(int(i) / 1024) + 0.0001 for i in  re.findall(r"mem_heap_extra_B=(\d*)", content)]
  memStackB = [(int(i) / 1024) + 0.0001 for i in  re.findall(r"mem_stacks_B=(\d*)", content)]

  # Plot the memory information.
  X = list(range(len(memHeapExtraB)))
  X = [x+0.0001 for x in X]


  build = str(abs(hash(datetime.datetime.now())+hash(datetime.datetime.now())))

  fileName = 'graphs/memory_' + str(build)

  header = 'dummy,' + str(X)[1:-1] + '\n'

  # Write the csv file that contains the data.
  with open('reports/' + fileName + '.csv', 'wb+') as fid:
    fid.write(header.encode('UTF-8'))

    memHeapExtra = 'memHeapExtraB, ' + str(memHeapExtraB)[1:-1]  + '\n'
    fid.write(memHeapExtra.encode('UTF-8'))

    memHeapB = 'memHeapB, ' + str(memHeapB)[1:-1]  + '\n'
    fid.write(memHeapB.encode('UTF-8'))

    memStackB = 'memStackB, ' + str(memStackB)[1:-1]
    fid.write(memStackB.encode('UTF-8'))

  content = {}
  content['container'] = build
  content['type'] = 'area'
  content['title'] = datasetName
  content['subtitle'] = 'Hide data series by clicking the legend item.'
  content['xAxisLabels'] = 'false'
  content['xAxisRotation'] = '0' if len(header) < 130 else '-45'
  content['yAxis'] = 'memory [KB]'
  content['tooltipText'] = 'KB'
  content['data'] = fileName + '.csv'

  with open('reports/' + fileName + '.js', 'wb+') as fid:
      c = chartTemplate % content
      fid.write(c.encode('UTF-8'))

  return (fileName + '.js', build)

'''
Create the top line chart.

@param db - The database object.
@return The filename of the line chart.
'''
def CreateTopLineChart(db):
  # Generate a list of scalar values. Use the privious or next elemnt to fill
  # the gap.
  def NormalizeData(data):
    i = 0
    while len(data) != i:
      if not data[i]:
        if i > 0 and data[i - 1]:
          data[i] = data[i - 1]
        else:
          del data[i]
          i -= 1
      i += 1
    return data

  build = str(abs(hash(datetime.datetime.now())))

  res = db.GetLibraryIds()
  if res:
    header = ''
    sums = []

    i = 1
    for id, name in res:
      if 'memory' not in name:
        # Add library name to the header.
        header += str(i) + ','

        i += 1

        # Add the calcuated sum over all timing data for the specified data
        # to the list.
        lsum = db.GetResultsSum(name)
        if lsum:
          sums.append(lsum[1])
        else:
          sums.append([])


    # Remove the last comma from the header.
    if header:
      header = 'dummy,' + header[:-1] + '\n'

    fileName = 'graphs/top_' + str(build)
    # Write the csv file that contains the data.
    with open('reports/' + fileName + '.csv', 'wb+') as fid:
      # Write header line to file.
      fid.write(header.encode('UTF-8'))

      # Normalize data and fill existing gaps.
      lenSum = [len(x) for x in sums]
      for i, sum in enumerate(sums):
        sum = NormalizeData(sum)
        while len(sum) < max(lenSum):
          sum.append(sum[-1])

        c = str(res[i][1]) + ', ' + str(sum)[1:-1]
        if i < len(sums) - 1:
          c += '\n'

        fid.write(c.encode('UTF-8'))

    content = {}
    content['container'] = build
    content['type'] = 'area'
    content['title'] = 'Overall Timing'
    content['subtitle'] = 'Hide data series by clicking the legend item.'
    content['xAxisLabels'] = 'true'
    content['xAxisRotation'] = '0' if len(header) < 130 else '-45'
    content['yAxis'] = 'Time [s]'
    content['tooltipText'] = 's'
    content['data'] = fileName + '.csv'

    with open('reports/' + fileName + '.js', 'wb+') as fid:
      c = chartTemplate % content
      fid.write(c.encode('UTF-8'))

    return (fileName + '.js', build)
  else:
    return ''
