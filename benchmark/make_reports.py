'''
  @file make_reports.py
  @author Marcus Edel

  Functions to generate the reports.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains
# symlinks to modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], '../util')))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from graph import *
from parser import *
from log import *
from database import *
from template import *
from misc import *
from profiler import *

import argparse
import glob
import re
import collections

'''
Create the top line chart.

@param db - The database object.
@return The filename of the line chart.
'''
def CreateTopLineChart(db, topChartColor):
  res = db.GetResultsSum("mlpack")
  if res:
    build, results = res
  else:
    return ""

  GenerateSingleLineChart(results, "reports/img/mlpack_top_" + str(build) + 
      ".png", backgroundColor=topChartColor, windowWidth=9, windowHeight=1.6)
  return "img/mlpack_top_" + str(build) + ".png"

'''
Create the timings table.

@param data - Dictionary which contains the timings.
@libraries - List which contains the library names.
@return HTML code which contains the header and the timing data.
'''
def CreateTimingTable(data, libraries):
  # Create the table header.
  header = ""
  for library in libraries:
    header += "<th>" + library + "</th>"

  # Create the table timing content.
  timingTable = ""
  for dataset, timings in data.items():
    timingTable += "<tr><td>" + dataset + "</td>"
    for time in timings:

      # Highlight the data with the best timing.
      if minData(timings) == time:
        time = str("{0:.4f}".format(time)) + "s" if isFloat(str(time)) else time
        timingTable += '<td><p class="text-success"><strong>' + time 
        timingTable += "</strong></p></td>"
      else:
        time = str("{0:.4f}".format(time)) + "s" if isFloat(str(time)) else time
        timingTable += "<td>" + time + "</td>"

    timingTable += "</tr>"

  return (header, timingTable)

'''
Create the table with the datasets informations.

@param resultList - List of a list which contains the dataset informations.
@return HTML code which contains the dataset informations.
'''
def CreateDatasetTable(resultList):
  datasets = []
  datasetTable = ""
  for results in resultList:
    results = results[0]
    for result in results:
      for data in result:
        datasetName = data[8]

        if datasetName not in datasets:
         datasets.append(datasetName)

         # Dataset name.
         datasetTable += "<tr><td>" + datasetName + "</td>"
         # Dataset disksize.
         datasetTable += "<td>" + "{0:.5f}".format(data[9]) + " MB</td>"
         # Number of instances.
         datasetTable += "<td>" + str(data[10]) + "</td>"
         # Number of attributes.
         datasetTable += "<td>" + str(data[11]) + "</td>"
         # Number of instances * number of attributes.
         datasetTable += "<td>" + str(data[10] * data[11]) + "</td>"
         # Attribute type.
         datasetTable += "<td>" + str(data[12]) + "</td>"
         datasetTable += "</tr>"

  return datasetTable

'''
Create the content for the memory section.

@param results - This data structure contains the memory results.
@return A string that contains the content for the memory section.
'''
def CreateMemoryContent(results, chartColor):
  memoryContent = ""
  if results:
    for result in results:
      memoryValues = {}
      memoryValues["name"] = result[7]
      memoryValues["nameID"] = result[7] + str(hash(datetime.datetime.now()))
      
      content = Profiler.MassifMemoryUsageReport(str(result[5]))
      try:
        content = content.decode()
      except AttributeError:
        pass
      memoryValues["content"] = content

      filename = "img/massif_" + os.path.basename(result[5]).split('.')[0] + ".png"
      CreateMassifChart(result[5], "reports/" + filename, chartColor)
      memoryValues["memoryChart"] = filename

      memoryContent += memoryPanelTemplate % memoryValues

  return memoryContent

'''
Create the method info content.

@param results - Contains the method information.
@param methodName - The name of the method.
@return A string that contains the method information HTML code.
'''
def CreateMethodInfo(results, methodName):
  methodInfo = ""
  if results:
    infoValues = {}
    infoValues["name"] = methodName
    infoValues["nameID"] = methodName + str(hash(datetime.datetime.now()))
    content = results[0][2]
    try:
      content = content.decode()
    except AttributeError:
      pass

    infoValues["content"] = content
    methodInfo = panelTemplate % infoValues
  
  return methodInfo

'''
Create the method container with the information from the database.

@param db - The database object.
@return HTML code which contains the information for the container.
'''
def MethodReports(db, chartColor):
  methodsPage = ""
  numDatasets = 0

  # Get the latest builds.
  libraryIds  = db.GetLibraryIds()
  buildIds = []
  for libraryid in libraryIds:
    buildIds.append((db.GetLatestBuildFromLibary(libraryid[0]), libraryid[1]))
  
  methodGroup = {}
  # Iterate throw all methods and create for each method a new container.
  for method in db.GetAllMethods():
    
    methodResults = []
    methodLibararies = []
    resultBuildId = []
    for buildId in buildIds:
      results = db.GetMethodResultsForLibary(buildId[0], method[0])

      if results:
        methodLibararies.append(buildId[1])
        resultBuildId.append(buildId[0])
        methodResults.append(results)

    if methodResults:
      t = (methodResults, methodLibararies, resultBuildId)
      if method[1] in methodGroup:
        methodGroup[method[1]].append(t)
      else:
        methodGroup[method[1]] = [t]

  methodGroup = collections.OrderedDict(sorted(methodGroup.items()))
  collapseGroup = 0
  for methodName, results in methodGroup.items():
    # Create the container.
    reportValues = {}
    reportValues["methodName"] = methodName
    
    resultPanel = ""
    methodInfo = ""
    memoryContent = ""

    mlpackMemoryId = db.GetLibrary("mlpack_memory")
    mlpackMemoryBuilId = ""
    if mlpackMemoryId:
        mlpackMemoryBuilId = db.GetLatestBuildFromLibary(mlpackMemoryId[0][0])

    # Variables to count the status informations.
    failureCount = 0
    datasetCount = 0
    timeoutCount = 0
    bestLibCount = 0
    totalTimeCount = 0
    libCount = 0

    for result in results:
      resultValues = {}
      groupPanel = {}
      
      methodResults = result[0]
      methodLibararies = result[1]
      resultBuildId = result[2]
      methodId = methodResults[0][0][6]

      # Generate a "unique" hash for the chart name.
      chartHash = str(hash(str(result)))

      # Generate a "unique" name for the line chart.
      lineChartName = "img/line_" + chartHash + ".png"

      res = db.GetResultsMethodSum("mlpack", methodId)
      if res:
        build, methodResultsSum = res
      else:
        continue

      GenerateSingleLineChart(methodResultsSum, "reports/" + lineChartName, 
          chartColor)

      # Generate a "unique" name for the bar chart.
      barChartName = "img/bar_" + chartHash + ".png"

      # Create the bar chart.
      ChartInfo = GenerateBarChart(results=methodResults, 
          libraries=methodLibararies, fileName="reports/" + barChartName, 
          backgroundColor=chartColor)

      numDatasets, totalTime, failure, timeouts, bestLibnum, timingData = ChartInfo

      # Increase the status information.
      failureCount += failure
      datasetCount += numDatasets
      timeoutCount += timeouts
      bestLibCount += bestLibnum
      totalTimeCount += totalTime

      header, timingTable = CreateTimingTable(timingData, methodLibararies)

      libCount = libCount if libCount >= len(methodLibararies) else len(methodLibararies)

      parameters = db.GetMethodParameters(methodId)
      if parameters:
        parameters = parameters[0][0]
      else:
        parameters = ""

      resultValues["parameters"] = lineChartName
      resultValues["lineChart"] = lineChartName
      resultValues["barChart"] = barChartName
      resultValues["timingHeader"] = header
      resultValues["timingTable"] = timingTable

      groupPanel["nameID"] = chartHash
      groupPanel["name"] = "Parameters: " + (parameters if parameters else "None")
      groupPanel["content"] = resultsPanel % resultValues

      resultPanel += resultsTemplate % groupPanel

      # Create the memory content.
      if mlpackMemoryBuilId:
        memoryResults = db.GetMemoryResults(mlpackMemoryBuilId, 
            mlpackMemoryId[0][0], methodId)

        groupPanel["content"] = CreateMemoryContent(memoryResults, chartColor)
        if groupPanel["content"]:
          groupPanel["nameID"] = chartHash + "_m"
          groupPanel["name"] = "Parameters: " + (parameters if parameters else "None")
          
          memoryContent += resultsTemplate % groupPanel

      # Create the method info content.
      if not methodInfo:
        methodInfo = CreateMethodInfo(db.GetMethodInfo(methodId), methodName)
      
    datasetTable = CreateDatasetTable(results)

    # Calculate the percent for the progress bar.
    if numDatasets != 0:
      negative = (((datasetCount - bestLibCount) / float(datasetCount)) * 100.0)
      reportValues["progressPositive"] = "{0:.2f}".format(100 - negative) + "%"

      if negative == 0:
        reportValues["progressPositiveStyle"] = "{0:.2f}".format(100 - negative) + progressBarStyle
      else:
        reportValues["progressPositiveStyle"] = "{0:.2f}".format(100 - negative) + "%;"

      if negative == 100:
        reportValues["progressNegativeStyle"] = "{0:.2f}".format(negative) + progressBarStyle
      else:
        reportValues["progressNegativeStyle"] = "{0:.2f}".format(negative) + "%;"
    else:
      reportValues["progressPositive"] = "0%"
      reportValues["progressPositiveStyle"] = "0%;"
      reportValues["progressNegativeStyle"] = "100%" + progressBarStyle
    
    reportValues["numLibararies"] = libCount
    reportValues["numDatasets"] = datasetCount
    reportValues["totalTime"] =  "{0:.2f}".format(totalTimeCount)
    reportValues["failure"] = failureCount
    reportValues["timeouts"] = timeoutCount
    reportValues["datasetTable"] = datasetTable
    reportValues["memoryContent"] = memoryContent
    reportValues["methodInfo"] = methodInfo
    reportValues["resultsPanel"] = resultPanel
    reportValues["methods"] = len(results)
    reportValues["groupOne"] = collapseGroup
    reportValues["groupTwo"] = collapseGroup + 1
    reportValues["groupThree"] = collapseGroup + 2

    methodsPage += methodTemplate % reportValues

    # Increase the collapse group id.
    collapseGroup += 3

  return methodsPage

'''
Search the highest index_[number].html number.

@return The highest index_number.html number and the file count.
'''
def GetMaxIndex():
  files = glob.glob("reports/index*.html")

  maxId = 0
  for f in files:
    pattern = re.compile(r"""
        .*?index_(?P<id>.*?).html
        """, re.VERBOSE|re.MULTILINE|re.DOTALL)
    
    match = pattern.match(f)
    if match:
      i = int(match.group("id"))
      if i > maxId:
        maxId = i
  return (maxId, len(files))

'''
Adjust the pagination for all index.html files.

@param maxFiles - The number of files to keep.
'''
def AdjustPagination(maxFiles):
  maxId, files = GetMaxIndex()

  delFiles = []
  if maxId >= maxFiles:
    maxId -= 1

  for i in range(1, files + 1):
    try:
      with open("reports/index_" + str(i) + ".html", "r+") as fid:
        content = fid.read()
        pattern = '<ul class="pagination">'
        pos = content.rfind(pattern)
        content = content[:pos+len(pattern)]

        # If i equals one there is no previous index file. In this case we can't
        # create a link to the previous index file.
        if i == 1:
          content += '<li class="previous"><a href="index.html">&larr; Newer</a></li>\n'
        else:
          content += '<li class="previous"><a href="index_' + str(i - 1) + '.html">&larr; Newer</a></li>\n'
        
        # If i equals maxId there is no next index file. In this case we can't
        # create a link to the next index file.
        if i == maxId:
          content += '<li class="next disabled"><a href="#">Older &rarr;</a></li>'
        else:
          content += '<li class="next"><a href="index_' + str(i + 1) + '.html">Older &rarr;</a></li>\n'

        content += paginationTemplate
        # Reset the file descriptor.
        fid.seek(0)
        # Set the new pagination.
        fid.write(content)
        fid.truncate()

        # Delete unneeded files. We don't want to store all reports, for that 
        # reason we delete the oldest report.
        if i < maxFiles:
          delFiles.extend(re.findall('src="img/(.*?)"', content))
        else:
          c = re.findall('src="img/(.*?)"', content)
          delFiles = ["reports/img" + img for img in c if img not in delFiles]
          delFiles.append("reports/index_" + str(i) + ".html")
          fid.close()
          RemoveDataset(delFiles)
    except IOError as e:
      Log.Fatal("Exception: " + str(e))
      return

'''
Get the pagination for the new index.html file.

@return The new pagination as HTML code.
'''
def NewPagination():
  maxId, files = GetMaxIndex()

  # This is the new index file, for that reason there is never a link to a 
  # previous index file.
  pagination = '<li class="previous disabled"><a href="#">&larr; Newer</a></li>\n'
  # If i is greater then maxId there is no next index file. In this case we 
  # can't create a link to the next index file.
  if maxId > 0:
    pagination += '<li class="next"><a href="index_1.html">Older &rarr;</a></li>\n'
  else:    
    pagination += '<li class="next disabled"><a href="#">Older &rarr;</a></li>'

  return pagination

'''
Rename the index_[number].html files.
'''
def ShiftReports(): 
  maxId, files = GetMaxIndex()

  # Iterate through all index_[number].html files and increase the number.
  for i in range(files, 0, -1):
    fileName = "reports/index_" + str(i) + ".html"
    if CheckFileAvailable(fileName):
        os.rename(fileName, "reports/index_" + str(i + 1) + ".html")

  # The old index.html file in the new index_1.html file.
  fileName = "reports/index.html"
  if CheckFileAvailable(fileName):
    os.rename(fileName, "reports/index_1.html")

'''
Create the new report.

@param configfile - Create the reports with the given configuration file.
'''
def Main(configfile):
  # Report settings.
  database = "reports/benchmark.db"
  keepReports = 3
  topChartColor = "#F3F3F3"
  chartColor = "#FFFFFF"

  # Create the folder structure.
  CreateDirectoryStructure(["reports/img", "reports/etc"])

  # Read the config.
  config = Parser(configfile, verbose=False)
  streamData = config.StreamMerge()

  # Read the general block and set the attributes.
  if "general" in streamData:
    for key, value in streamData["general"]:
      if key == "database":
        database = value
      elif key == "keepReports":
        keepReports = value
      elif key == "topChartColor":
        topChartColor = value
      elif key == "chartColor":
        chartColor = value

  db = Database(database)
  db.CreateTables()

  ShiftReports()
  AdjustPagination(keepReports)

  # Get the values for the new index.html file.
  reportValues = {}
  reportValues["topLineChart"] = CreateTopLineChart(db, topChartColor)
  reportValues["pagination"] = NewPagination()
  reportValues["methods"] = MethodReports(db, chartColor)

  template = pageTemplate % reportValues

  # Write the new index.html file.
  with open("reports/index.html", 'w') as fid:
    fid.write(template)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="""Perform the memory benchmark 
      with the given config.""")
  parser.add_argument('-c','--config', help='Configuration file name.', 
      required=True)

  args = parser.parse_args()

  if args:
    Main(args.config)
  