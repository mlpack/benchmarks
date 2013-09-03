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

import numpy as np
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import re
import collections


# Use this colors to plot the graph.
colors = ['#3366CC', '#DC3912', '#FF9900', '#FFFF32', '#109618', '#990099', 
          '#DD4477', '#AAAA11', '#22AA99']

'''
Generate a bar chart with the specified informations.

@param results - Contains the values to plot.
@param libraries - A list that contains the names of the libraries.
@param fileName - The filename of the line chart.
@param bestlib - The name of the library which should be compared with the other
libraries.
@param backgroundColor - The color of the image background.
'''
def GenerateBarChart(results, libraries, fileName, bestlib="mlpack", 
    backgroundColor="#FFFFFF"):
  # Bar chart settings.
  lineWidth = 0.1
  barWidth = 0.15
  opacity = 0.9
  fill = True
  windowWidth = 8.1
  windowHeight = 3.3
  gridLineWidth = 0.2

  # Create figure and set the color.
  matplotlib.rc('axes', facecolor=backgroundColor)
  matplotlib.rcParams.update({'font.size': 8})
  fig = plt.figure(figsize=(windowWidth, windowHeight), 
      facecolor=backgroundColor, dpi=100)
  plt.rc('lines', linewidth=lineWidth)
  ax = plt.subplot(1,1,1)

  # Set the grid style.
  ax.yaxis.grid(True, linestyle='-', linewidth=gridLineWidth)
  ax.xaxis.grid(False)
  ax.spines['left'].set_visible(False)
  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.get_xaxis().tick_bottom()
  ax.get_yaxis().tick_left()
  ax.spines['bottom'].set_linewidth(gridLineWidth)

  # Data structures to set the legend and the right postions for the bar chart.
  legendIndex = []
  color = {}
  chartHandler = []
  legendNames = []
  nextBar = 0
  legendPosition = 0
  legendBegin = 0
  
  # use this variable to count the time.
  totalTime = 0
  # Use this variable to count the timeouts.
  timeouts = 0
  # Use this variable to count the failures.
  failure = 0

  # Use this data structures to generate the timing table and the progress bar.
  bestTiming = {}
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
      bestTiming[dataset] = (time, libraries[l])
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

  for key, values in timingData.items():
    l = 0
    legendIndex.append(nextBar)
    for value in values:
      color = colors[l % len(colors)]

      if isFloat(value):
        plt.bar(nextBar, value, barWidth, alpha=opacity, color=color, 
            fill=fill,lw=0.2)
      else:
        plt.bar(nextBar, maxValue, barWidth, alpha=opacity, color="gray", 
            fill=fill, lw=0.2)

      time = value if isFloat(value) else 10

      nextBar += barWidth
      l += 1
    nextBar += (4 * barWidth)

  # Create a proxy artist for the legend.
  handler = []
  for l, library in enumerate(libraries):
    color = colors[l % len(colors)]
    handler.append(plt.Rectangle((0, 0), 1, 1, fc=color, alpha=0.6))

  handler.append(plt.Rectangle((0, 0), 1, 1, fc="gray", alpha=0.6))

  # Set the labels for the x-axis.
  plt.xticks(legendIndex , list(timingData.keys()), rotation=30, ha='right')

  # Set the color and the font of the x-axis and y-axis labels.
  ax.tick_params(axis='both', which='major', labelsize=8, labelcolor="#6e6e6e")
  ax.tick_params(axis='both', which='minor', labelsize=6, labelcolor="#6e6e6e")

  # Create the legend above the bar chart.
  lgd = ax.legend(handler, libraries + ["failure/ timeout"], loc='upper center', 
    bbox_to_anchor=(0.5, 1.3 + (0.2 * len(libraries) / 6)), fancybox=True, 
    shadow=False, ncol=6, fontsize=8)
  lgd.get_frame().set_linewidth(0)
  for label in lgd.get_texts():
    label.set_color("#6e6e6e")

  # Set axis labels.
  plt.ylabel("time [s]", color="#6e6e6e")

  # Save the bar chart.
  fig.tight_layout()
  fig.savefig(fileName, bbox_extra_artists=(lgd,), bbox_inches='tight', 
    facecolor=fig.get_facecolor(), edgecolor='none', format='png', dpi=100)
  plt.close()

  # Count the time in which bestlib is the best.
  bestLibCount = 0
  for dataset, data in bestTiming.items():
    if data[1] == bestlib:
      bestLibCount += 1
  
  return (len(timingData), totalTime, failure, timeouts, bestLibCount, timingData)

'''
Generate a line chart with the specified informations.

@param data - List which contains the values for the line chart.
@param fileName - The filename of the line chart.
@param backgroundColor - The color of the image background.
'''
def GenerateSingleLineChart(data, fileName, backgroundColor="#FFFFFF", 
    windowWidth=8.1, windowHeight=1.3):
  def NormalizeData(data):
    i = 0
    while len(data) != i:
      if not data[i]:
        if i > 0 and data[i -1]:
          data[i] = data[i - 1]
        else:
          del data[i]
          i -= 1
      i += 1
    return data

  if not CheckFileAvailable(fileName):
    # Line chart settings.
    lineWidth = 1.5
    opacity = 0.9
    gridLineWidth = 0.2

    # Create figure and set the color.
    matplotlib.rc('axes', facecolor=backgroundColor)
    matplotlib.rcParams.update({'font.size': 8})
    fig = plt.figure(figsize=(windowWidth, windowHeight), 
        facecolor=backgroundColor, dpi=100)
    plt.rc('lines', linewidth=lineWidth)
    ax = plt.subplot(1,1,1)

    # Set the grid style.
    ax.yaxis.grid(True, linestyle='-', linewidth=gridLineWidth)
    ax.xaxis.grid(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    ax.spines['bottom'].set_linewidth(gridLineWidth)

    # Set ticks for the x-axis.
    myLocator = mticker.MultipleLocator(1)
    ax.xaxis.set_major_locator(myLocator)

    data = NormalizeData(data)

    # If we have only have a single value we don't want to start from zero so we 
    # double the data.
    if len(data) == 1:
      data += data
      
    # Create the data for the x-axis.
    X = np.arange(len(data))

    # Plot the line chart.
    plt.plot(X, data, color=colors[0], alpha=opacity, linewidth=1.7)

    # Set the color and the font of the x-axis and y-axis labels.
    ax.tick_params(axis='both', which='major', labelsize=8, labelcolor="#6e6e6e")
    ax.tick_params(axis='both', which='minor', labelsize=6, labelcolor="#6e6e6e")

    # Set axis labels.
    plt.ylabel("time [s]", color="#6e6e6e")
    plt.xlabel("benchmark build", color="#6e6e6e")

    # Save the line chart.
    fig.tight_layout()
    fig.savefig(fileName, bbox_inches='tight', facecolor=fig.get_facecolor(), 
        edgecolor='none', dpi=100)
    plt.close()

'''
Generate a memory chart with the specified informations.

@param massiflogFile - The massif logfile.
@param fileName - The filename of the memory chart.
@param backgroundColor - The color of the image background.
'''
def CreateMassifChart(massiflogFile, fileName, backgroundColor="#FFFFFF"):
  if not CheckFileAvailable(fileName):
    lineWidth = 1.5
    opacity = 0.9
    windowWidth = 8.1
    windowHeight = 1.3
    gridLineWidth = 0.2

    # Create figure and set the color.
    matplotlib.rc('axes', facecolor=backgroundColor)
    matplotlib.rcParams.update({'font.size': 8})
    fig = plt.figure(figsize=(windowWidth, windowHeight), 
        facecolor=backgroundColor, dpi=100)
    plt.rc('lines', linewidth=lineWidth)
    ax = plt.subplot(1,1,1)

    # Set the grid style.
    ax.yaxis.grid(True, linestyle='-', linewidth=gridLineWidth)
    ax.xaxis.grid(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    ax.spines['bottom'].set_linewidth(gridLineWidth)

    # Read the massif logfile.
    with open(massiflogFile, "r") as fid:
      content = fid.read()

    # Parse the massif logfile.
    memHeapB = [(int(i) / 1024) + 0.0001 for i in re.findall(r"mem_heap_B=(\d*)", content)]
    memHeapExtraB = [(int(i) / 1024) + 0.0001 for i in  re.findall(r"mem_heap_extra_B=(\d*)", content)]
    memStackB = [(int(i) / 1024) + 0.0001 for i in  re.findall(r"mem_stacks_B=(\d*)", content)]

    # Plot the memory information.
    X = np.arange(len(memHeapExtraB))
    X = [x+0.0001 for x in X]
    plt.fill_between(X, memHeapExtraB, 0, color="#109618", alpha=0.6)
    plt.fill_between(X, memHeapExtraB, memHeapB, color="#DC3912", alpha=0.6)
    plt.fill_between(X, memHeapExtraB, memStackB, color="#3366CC", alpha=0.6)

    # Set the color and the font of the x-axis and y-axis labels.
    ax.tick_params(axis='both', which='major', labelsize=8, labelcolor="#6e6e6e")
    ax.tick_params(axis='both', which='minor', labelsize=6, labelcolor="#6e6e6e")

    # Create a proxy artist, because fill_between hasn't a chart handler.
    p1 = plt.Rectangle((0, 0), 1, 1, fc="#109618", alpha=0.6)
    p2 = plt.Rectangle((0, 0), 1, 1, fc="#DC3912", alpha=0.6)
    p3 = plt.Rectangle((0, 0), 1, 1, fc="#3366CC", alpha=0.6)

    # Set axis labels.
    plt.ylabel("memory [KB]", color="#6e6e6e")
    plt.xlabel("snapshot", color="#6e6e6e")

    # Create the legend above the memory chart.
    lgd = ax.legend((p1, p2, p3), 
      ("mem heap B", "mem heap extra B", "mem stacks B"), loc='upper center', 
      bbox_to_anchor=(0.5, 1.3), fancybox=True, shadow=False, ncol=8, fontsize=8)
    lgd.get_frame().set_linewidth(0)
    for label in lgd.get_texts():
      label.set_color("#6e6e6e")
         
    # Save the memory chart.
    fig.tight_layout()
    fig.savefig(fileName, bbox_extra_artists=(lgd,), bbox_inches='tight', 
      facecolor=fig.get_facecolor(), edgecolor='none', format='png', dpi=100)
    plt.close()
