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
from system import *

import argparse, glob, re, collections, simplejson, codecs, random

'''
Create the timings table.

@param data - Dictionary which contains the timings.
@libraries - List which contains the library names.
@type - The type of the timing table ('metric' or 'timing').
@return HTML code which contains the header and the timing data.
'''
def CreateTimingTable(data, libraries, type):
  # Create the table header.
  header = ""
  for library in libraries:
    header += "<th>" + library + "</th>"

  # Create the table timing content.
  timingTable = ""
  for dataset, timings in data.items():
    timingTable += "<tr><td>" + dataset + "</td>"
    for time in timings:

      # Distinguish between the metric and the timing type.
      c = minData(timings) if type == 'timing' else maxData(timings)

      # Highlight the data with the best timing.
      if c == time:
        time = str("{0:.4f}".format(time)) + "s" if isFloat(str(time)) else time
        timingTable += '<td><p class="text-success"><strong>' + time
        timingTable += "</strong></p></td>"
      else:
        time = str("{0:.4f}".format(time)) + "s" if isFloat(str(time)) else time
        timingTable += "<td>" + time + "</td>"

    timingTable += "</tr>"

  return (header, timingTable)

def GetBootstrapTimingTable(results, libraries, datasetName):
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
            if time == 'failure' or '>' in str(time):
              time = '-'

            timingData[dataset][l] = time
          else:
            timingData[dataset] = ['-' for x in range(len(libraries))]
            timingData[dataset][l] = time

          # We can only plot scalar values so we jump over the other.
          if time == "failure":
            continue
          elif str(time).count(">") > 0:
            continue

    l += 1

  timingData = collections.OrderedDict(sorted(timingData.items()))

  keyCount = 0
  failureData = [0 for x in range(len(libraries))]
  for key, value in timingData.items():
    keyCount += 1

    pos = [i for i, x in enumerate(value) if x == '-']
    for p in pos:
      failureData[p] += 1

  return (timingData, failureData)

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
      if 'timing' in result:
        result = result["timing"]
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

def CreateBootstrapTable(result, libaries, counter):
  content = '<table class="table table-striped"><thead><tr><th></th>'

  for i in range(len(libaries)):
    if 4 <= (i + 1) <= 20 or 24 <= i <= 30:
      suffix = "TH"
    else:
        suffix = ["ST", "ND", "RD"][(i + 1) % 10 - 1]

    content += '<th>' + str(i + 1)  + suffix + '</th>'

  content += '</tr></thead><tbody>'

  for lib in libaries:
    # Name of the model.
    content += '<tr><td>' + lib + '</td>'
    for res in result[lib]:
      content += '<td>' + str(res /  counter) + '</td>'

    content += '</tr>'

  content += '</tbody></table>'
  return content

'''
Create the content for the memory section.

@param results - This data structure contains the memory results.
@return A string that contains the content for the memory section.
'''
def CreateMemoryContent(results):
  memoryContent = ""
  ids = ""

  if results:
    for result in results:
      memoryValues = {}
      # memoryValues["name"] = result[7]
      # memoryValues["nameID"] = result[7] + str(hash(datetime.datetime.now()))

      content = Profiler.MassifMemoryUsageReport(str(result[5]))
      try:
        content = content.decode()
      except AttributeError:
        continue
        pass

      fileName = 'memory/memory_' + result[7] + str(hash(result[5])) + '.txt'

      with open('reports/' + fileName, 'wb+') as fid:
        fid.write(content.encode('UTF-8'))

      chartInfo = CreateMassifChart(result[5], result[7])

      if not chartInfo:
        continue

      containerID, container = chartInfo
      memoryValues['container'] = container
      memoryValues['massifFilePath'] = fileName
      memoryValues['massifFile'] = result[7]

      ids += containerID + ","
      memoryContent += memoryPanelTemplate % memoryValues

  if ids:
    ids = ids[:-1]

  return (memoryContent, ids)

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
@param bootstrapCountb - The number of selections from the metric results.
@return HTML code which contains the information for the container.
'''
def MethodReports(db, bootstrapCount):
  methodsPage = ""
  numDatasets = 0

  # Get the latest builds.
  libraryIds  = db.GetLibraryIds()
  buildIds = []
  for libraryid in libraryIds:
    buildIds.append((db.GetLatestBuildFromLibary(libraryid[0])[0][0], libraryid[1]))

  methodGroup = {}
  # Iterate throw all methods and create for each method a new container.
  for method in db.GetAllMethods():

    methodResults = []
    methodLibarariesTiming = []
    methodLibarariesMetric = []
    methodLibarariesBootstrap = []

    resultBuildId = []
    for buildId in buildIds:
      timing_results = db.GetMethodResultsForLibary(buildId[0], method[0])

      metric_results = db.GetMethodMetricResultsForLibrary(buildId[0],
                                                           method[0])

      bootstrap_results = db.GetMethodBootstrapResultsForLibrary(buildId[0],
                                                                 method[0])

      results = {}
      if timing_results:
        results["timing"] = timing_results
        methodLibarariesTiming.append(buildId[1])

      if metric_results:
        results["metric"] = metric_results
        methodLibarariesMetric.append(buildId[1])

      if bootstrap_results:
        results["bootstrap"] = bootstrap_results
        methodLibarariesBootstrap.append(buildId[1])


      results["id"] = method[0]

      if 'timing' in results or 'metric' in results or 'bootstrap' in results:
        # methodLibararies.append(buildId[1])
        resultBuildId.append(buildId[0])
        methodResults.append(results)

    if methodResults:
      t = (methodResults,
           methodLibarariesTiming,
           methodLibarariesMetric,
           methodLibarariesBootstrap,
           resultBuildId)

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
    resultPanelMetric = ""
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
    ChartInfoTiming = None
    datasetNamesMetric = None
    bootstrapContent = None

    # Iterate through all results.
    for result in results:
      # Initialze the datastructures used to set the template values.
      resultValues = {}
      groupPanelTiming = {}
      groupPanelMetric = {}
      resultPanelBootstrap = {}
      resultValuesMetric = {}

      # Generate a list of timing results.
      methodResultsTiming = []
      for resTiming in result[0]:
        if 'timing' in resTiming:
          methodResultsTiming.append(resTiming["timing"])

      # Generate a list of metric results.
      methodResultsMetric = []
      for resMetric in result[0]:
        if 'metric' in resMetric:
          methodResultsMetric.append(resMetric["metric"])

      # Generate a list of bootstrap results.
      methodResultsBootstrap = []
      for resBootstrap in result[0]:
        if 'bootstrap' in resBootstrap:
          methodResultsBootstrap.append(resBootstrap["bootstrap"])

      # Names of the libaries that have timing or metric result.
      # print(result)
      methodLibarariesTiming = result[1]
      methodLibarariesMetric = result[2]
      methodLibarariesBootstrap = result[3]

      # The id of the current method.
      methodId = result[0][0]["id"]

      # Generate a "unique" hash for the chart name.
      chartHash = str(hash(str(result)))

      # Generate a "unique" name for the timing line chart.
      lineChartNameTiming = "img/line_" + chartHash + "_timing.png"

      # Generate a "unique" name for the metric line chart.
      lineChartNameMetric = "img/line_" + chartHash + "_metric.png"

      res = db.GetResultsMethodSum("mlpack", methodId)
      if res:
        build, methodResultsSum = res
      else:
        continue

      # use the method parameter as title for the panel.
      parameters = db.GetMethodParameters(methodId)
      parameters = parameters[0][0] if parameters else ''

      # Generate a "unique" name for the timing bar chart.
      barChartNameTiming = "img/bar_" + chartHash + "_timing.png"

      # Create the timing bar chart.
      ChartInfoTiming = GenerateBarChart(methodResultsTiming,
                                         methodLibarariesTiming,
                                         "reports/" + barChartNameTiming)

      # Increase the status information.
      failureCount += ChartInfoTiming[2]
      datasetCount += ChartInfoTiming[0]
      timeoutCount += ChartInfoTiming[3]
      bestLibCount += ChartInfoTiming[4]
      totalTimeCount += ChartInfoTiming[1]

      # Create the content for the timing table.
      headerTiming, timingTableTiming = CreateTimingTable(ChartInfoTiming[5],
                                                          methodLibarariesTiming,
                                                          'timing')

      # Set the number of libraries.
      libCount = libCount if libCount >= len(methodLibarariesTiming) else len(
          methodLibarariesTiming)

      # Set the parameters for the timing template.
      resultValues["container"] = ChartInfoTiming[7]
      resultValues["timingHeader"] = headerTiming
      resultValues["timingTable"] = timingTableTiming
      groupPanelTiming["nameID"] = chartHash + "t"
      groupPanelTiming["name"] = "Parameters: " + (parameters if parameters else "None")
      groupPanelTiming["content"] = resultsPanel % resultValues
      groupPanelTiming["containerID"] = ChartInfoTiming[6]

      # Get the datasets that have metric results.
      datasetNamesMetric = []
      for data in methodResultsMetric:
        for dataRes in data:
          if dataRes[3] != '{}':
            datasetNamesMetric.append(dataRes[7])

      # Get the datasets that have bootstrap results.
      datasetNamesBootstrap = []
      for data in methodResultsBootstrap:
        for dataRes in data:
          if dataRes[3] != '{}':
            datasetNamesBootstrap.append(dataRes[7])

      # Extract from the bootstrap results the values that we can use for
      # bootstraping.
      bootstrapMetricContainer = []
      bootstrapDatasetContainer = []
      for dataSetName in set(datasetNamesBootstrap):
        bootstrapTable, failureData = GetBootstrapTimingTable(
                                                 methodResultsBootstrap,
                                                 methodLibarariesBootstrap,
                                                 dataSetName)

        # We can't use the metric if not all libaries contain a value for this
        # dataset.
        bootstrapTableTemp = {}
        for key, value in bootstrapTable.items():
          if not '-' in value:
            bootstrapTableTemp[key] = value
        if bootstrapTableTemp:
          bootstrapDatasetContainer.append(dataSetName)
          bootstrapMetricContainer.append(bootstrapTableTemp)

      bootstrapContent = ""
      bootstrapResults = {}
      for lib in methodLibarariesBootstrap:
        bootstrapResults[lib] = [0 for x in range(len(methodLibarariesBootstrap))]

      if methodLibarariesBootstrap:
        for i in range(bootstrapCount):
          # Select a random dataset.
          random_idx = random.randrange(0, len(bootstrapDatasetContainer))

          # Select a random metric.
          metric = random.choice(list(bootstrapMetricContainer[random_idx].keys()))

          # Get the results from the selected metric.
          result = bootstrapMetricContainer[random_idx][metric]

          # Sort the metric results and return the index.
          sortedResult = sorted(range(len(result)), key=result.__getitem__, reverse=True)

          for i, lib in enumerate(methodLibarariesBootstrap):
            bootstrapResults[lib][sortedResult[i]] += 1

        bootstrapContent = CreateBootstrapTable(bootstrapResults,
                                                methodLibarariesBootstrap,
                                                bootstrapCount)

      if bootstrapContent:
        resultPanelBootstrap["containerID"] = ""
        resultPanelBootstrap["nameID"] = chartHash + 'b'
        resultPanelBootstrap["name"] = "Bootstrap"
        resultPanelBootstrap["content"] = bootstrapContent
        bootstrapContent = resultsTemplate % resultPanelBootstrap

      # Set the parameters for the metric template.
      groupPanelMetric["nameID"] = chartHash + "m"
      groupPanelMetric["name"] = "Parameters: " + (parameters if parameters else "None")

      # Iterate through the datasets and set the other template values.
      groupPanelMetric["content"] = ""
      groupPanelMetric["containerID"] = ""
      for dataSetName in set(datasetNamesMetric):
        # Generate a "unique" name for the metric bar chart.
        barChartNameMetric = "img/bar_" + chartHash + "_metric_" + dataSetName + ".png"

        # Generate the metrics bar chart.
        ChartInfoMetric = GenerateBarChartMetric(methodResultsMetric,
                                                 methodLibarariesMetric, "reports/" +
                                                 barChartNameMetric, dataSetName)

        # Create the content for the metric timing table.
        headerMetric, timingTableMetric = CreateTimingTable(ChartInfoMetric[5],
                                                            methodLibarariesMetric,
                                                            'metric')
        # Set the parameters for the metric template.
        resultValuesMetric["timingHeader"] = headerMetric
        resultValuesMetric["timingTable"] = timingTableMetric
        resultValuesMetric["container"] = ChartInfoMetric[7]
        groupPanelMetric["content"] += resultsPanel % resultValuesMetric
        groupPanelMetric["containerID"] += ChartInfoMetric[6] + ','

        # Increase the status information.
        failureCount += ChartInfoMetric[2]
        timeoutCount += ChartInfoMetric[3]
        bestLibCount += ChartInfoMetric[4]

      resultPanel += resultsTemplate % groupPanelTiming

      if datasetNamesMetric:
        groupPanelMetric["containerID"] = groupPanelMetric["containerID"][:-1]
        resultPanelMetric += resultsTemplate % groupPanelMetric

      # Create the memory content.
      if mlpackMemoryBuilId:
        memoryResults = db.GetMemoryResults(mlpackMemoryBuilId,
            mlpackMemoryId[0][0], methodId)

        groupPanelTiming["content"], ids = CreateMemoryContent(memoryResults)

        if groupPanelTiming["content"]:
          groupPanelTiming["nameID"] = chartHash + "_m"
          groupPanelTiming["name"] = "Parameters: " + (parameters if parameters else "None")
          groupPanelTiming["containerID"] = ids

          memoryContent += resultsTemplate % groupPanelTiming

      # Create the method info content.
      if not methodInfo:
        methodInfo = CreateMethodInfo(db.GetMethodInfo(methodId), methodName)

    # Create the dataset table content.
    datasetTable = CreateDatasetTable(results)

    # Calculate the percent for the progress bar.
    if ChartInfoTiming and ChartInfoTiming[0] != 0:
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

    # Set the parameters for the panel informations.
    reportValues["numLibararies"] = libCount
    reportValues["numDatasets"] = datasetCount
    reportValues["totalTime"] =  "{0:.2f}".format(totalTimeCount)
    reportValues["failure"] = failureCount
    reportValues["timeouts"] = timeoutCount
    reportValues["datasetTable"] = datasetTable
    reportValues["memoryContent"] = memoryContent
    reportValues["methodInfo"] = methodInfo
    reportValues["resultsPanel"] = resultPanel

    # Don't add an empty metric panel.
    if datasetNamesMetric:
      reportValues["MetricResultsPanel"] = '<div><div class="panel panel-default"><div class="panel-heading">Metric Results</div>'
      reportValues["MetricResultsPanel"] += '<div class="panel-body">' + resultPanelMetric + '</div></div></div>'
    else:
      reportValues["MetricResultsPanel"] = ""
      reportValues["resultsPanelMetric"] = ""

    if bootstrapContent:
      reportValues["resultsPanelBootstrap"] = '<div><div class="panel panel-default"><div class="panel-heading">Bootstrap Results</div>'
      reportValues["resultsPanelBootstrap"] += '<div class="panel-body">' + bootstrapContent + '</div></div></div>'
    else:
      reportValues["resultsPanelBootstrap"] = ""

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
      with codecs.open("reports/index_" + str(i) + ".html", "r+", 'utf-8') as fid:
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
  # Default report settings.
  database = "reports/benchmark.db"
  keepReports = 3
  bootstrapCount = 10
  libraries = []

  # Create the folder structure.
  CreateDirectoryStructure(["reports/img",
                            "reports/etc",
                            "reports/graphs",
                            "reports/memory"])

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
      elif key == "libraries":
        libraries = value
      elif key == "version":
        version = value
      elif key == "bootstrap":
        bootstrapCount = value

  # Create a database object and create the necessary tables.
  db = Database(database)
  db.CreateTables()

  # Rename the old index files.
  ShiftReports()

  # Adjust the pagination in the existing index files.
  AdjustPagination(keepReports)

  # Get the values for the new index.html files.
  reportValues = {}
  chartInfoTop = CreateTopLineChart(db)

  reportValues["CPUModel"] =  SystemInfo.GetCPUModel()
  reportValues["Distribution"] =  SystemInfo.GetDistribution()
  reportValues["Platform"] =  SystemInfo.GetPlatform()
  reportValues["Memory"] =  SystemInfo.GetMemory()
  reportValues["CPUCores"] =  SystemInfo.GetCPUCores()

  reportValues["LibraryInformation"] = ""
  for i, libary in enumerate(libraries):
    information = {}
    information["name"] = libary
    information["version"] = version[i]
    reportValues["LibraryInformation"] += LibraryInformation % information

  reportValues["container"] = chartInfoTop[1]
  reportValues["pagination"] = NewPagination()
  reportValues["methods"] = MethodReports(db, bootstrapCount)
  reportValues["scripts"] = '<script src="' + chartInfoTop[0] + '"></script>'

  template = pageTemplate % reportValues

  # Write the new index.html file.
  with open("reports/index.html", 'wb') as fid:
    fid.write(template.encode('UTF-8'))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="""Perform the memory benchmark
      with the given config.""")
  parser.add_argument('-c','--config', help='Configuration file name.',
      required=True)

  args = parser.parse_args()

  if args:
    Main(args.config)
