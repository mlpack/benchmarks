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

import argparse
import glob
import re

'''
Create the top line chart.

@param db - The Database object.
@return The filename of the line chart.
'''
def CreateTopLineChart(db):
  build, results = db.GetResultsSum("mlpack")

  GenerateSingleLineChart(results, "reports/img/mlpack_top_" + str(build) + ".png")
  return "img/mlpack_top_" + str(build) + ".png"

'''
Create the table with the timings.

@param data - Dictionary which contains the timing data.
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
        time = str(time) + "s" if isFloat(time) else time 
        timingTable += '<td><p class="text-success"><strong>' + time + '</strong></p></td>'
      else:
        time = str(time) + "s" if isFloat(time) else time 
        timingTable += "<td>" + time + "</td>"

    timingTable += "</tr>"    

  return (header, timingTable)

'''
Create the table with the datasets informations.

@results List of a List which contains the datasets informations.
@return HTML code which contains the dataset informations.
'''
def CreateDatasetTable(results):
  datasets = []
  datasetTable = ""

  for result in results:
    for data in result:
      datasetName = data[8]

      if datasetName not in datasets:
       datasets.append(datasetName)

       datasetTable += "<tr><td>" + datasetName + "</td>"
       datasetTable += "<td>" + "{0:.5f}".format(data[9]) + " MB</td>"
       datasetTable += "<td>" + str(data[10]) + "</td>"
       datasetTable += "<td>" + str(data[11]) + "</td>"
       datasetTable += "<td>" + str(data[12]) + "</td>"
       datasetTable += "</tr>"

  return datasetTable

'''
Create the method container with the informations from the database.

@param db - The database object.
@return HTML code which contains the information for the container.
'''
def MethodReports(db):
  methodsPage = ""

  # Get the latest builds.
  libraryIds  = db.GetLibraryIds()
  buildIds = []
  for libraryid in libraryIds:
    buildIds.append((db.GetLatestBuildFromLibary(libraryid[0]), libraryid[1]))  

  # Iterate throw all methods and create for each method a new container.
  for method in db.GetAllMethods():
    methodResults = []
    methodLibararies = []
    for buildId in buildIds:
      results = db.GetMethodResultsForLibary(buildId[0], method[0])

      if results:        
        methodLibararies.append(buildId[1])
        methodResults.append(results)

    if methodResults:
      # Generate a "unique" hash for the chart names.
      chartHash = str(hash(str(method[1:]) + str(buildIds)))

      # Generate a "unique" name for the line chart.
      lineChartName = "img/line_" + chartHash + ".png"

      # Create the line chart.
      build, methodResultsSum = db.GetResultsMethodSum("mlpack", method[0])
      GenerateSingleLineChart(methodResultsSum, "reports/" + lineChartName)

      # Generate a "unique" name for the bar chart.
      barChartName = "img/bar_" + chartHash + ".png"
      
      # Create the bar chart.
      ChartInfo = GenerateBarChart(methodResults, methodLibararies, 
          "reports/" + barChartName)
      numDatasets, totalTime, failure, timeouts, bestLibCount, timingData = ChartInfo

      # Create the timing table.
      header, timingTable = CreateTimingTable(timingData, methodLibararies)
      datasetTable = CreateDatasetTable(methodResults)

      # Create the container.
      reportValues = {}
      reportValues["methodName"] = str(method[1:][0])
      reportValues["parameters"] = str(method[1:][1]) if method[1:][1] else "None"

      # Calculate the percent for the progress bar.
      negative = (((numDatasets - bestLibCount) / float(numDatasets)) * 100.0)
      reportValues["progressPositive"] = "{0:.2f}".format(100 - negative) + "%"
      reportValues["progressNegative"] = "{0:.2f}".format(negative) + "%"

      reportValues["barChart"] = barChartName
      reportValues["lineChart"] = lineChartName
      reportValues["numLibararies"] = str(len(methodLibararies))
      reportValues["numDatasets"] = numDatasets
      reportValues["totalTime"] = totalTime
      reportValues["failure"] = failure
      reportValues["timeouts"] = timeouts
      reportValues["timingHeader"] = header
      reportValues["timingTable"] = timingTable
      reportValues["datasetTable"] = datasetTable

      methodsPage += methodTemplate % reportValues

  return methodsPage

'''
Search the highest index_number.html number.

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
'''
def AdjustPagination():
  maxId, files = GetMaxIndex()

  for i in range(1, files + 1):
    with open("reports/index_" + str(i) + ".html", "r+") as fid:
      content = fid.read()
      pattern = '<ul class="pagination">'
      pos = content.rfind(pattern)
      content = content[:pos+len(pattern)]

      if i == 1:
        content += '<li><a href="index.html">&laquo;</a></li>\n'
      else:
        content += '<li><a href="index_' + str(i - 1) + '.html">&laquo;</a></li>\n'
      
      if i == maxId:
        content += '<li><a href="#">&raquo;</a></li>'
      else:
        content += '<li><a href="index_' + str(i + 1) + '.html">&raquo;</a></li>\n'

      content += paginationTemplate
      fid.seek(0)
      fid.write(content)
      fid.truncate()  

'''
Get the pagination for the new index.html file.

@return The new pagination as HTML code.
'''
def NewPagination():
  maxId, files = GetMaxIndex()

  pagination = '<li><a href="#">&laquo;</a></li>\n'
  if maxId > 0:
    pagination += '<li><a href="index_1.html">&raquo;</a></li>\n'
  else:    
    pagination += '<li><a href="#">&raquo;</a></li>'

  return pagination

'''
Rename the index_number.html files.
'''
def ShiftReports(): 
  maxId, files = GetMaxIndex()
  if maxId > 0 and os.path.isfile("reports/index.html"):
    os.rename("reports/index.html", "reports/index_" + str(maxId + 1) + ".html")
  elif files > 0 and os.path.isfile("reports/index.html"):
    os.rename("reports/index.html", "reports/index_1.html")

'''
Create the new report.

@param configfile - Create the reports with the given configuration file.
'''
def Main(configfile):
  # Reports settings.
  database = "reports/benchmark.db"

  # Read Config.
  config = Parser(configfile, verbose=False)
  streamData = config.StreamMerge()

  # Read the general block and set the attributes.
  if "general" in streamData:
    for key, value in streamData["general"]:
      if key == "database":
        database = value

  db = Database(database)

  ShiftReports()
  AdjustPagination()

  # Get the values for the new index.html file.
  reportValues = {}
  reportValues["topLineChart"] = CreateTopLineChart(db)
  reportValues["pagination"] = NewPagination()
  reportValues["methods"] = MethodReports(db)

  template = pageTemplate % reportValues

  # Write the new index.html file.
  with open("reports/index.html", 'w') as fid:
    fid.write(template)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="""Perform the benchmark with the
      given config.""")
  parser.add_argument('-c','--config', help='Configuration file name.', 
      required=True)

  args = parser.parse_args()

  if args:
    Main(args.config)
  