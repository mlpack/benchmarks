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
'''
def GenerateBarChart(results, libraries, fileName, bestlib="mlpack"):
  # Bar chart settings.
  lineWidth = 0.1
  barWidth = 0.15
  opacity = 0.9
  fill = True
  windowWidth = 11
  windowHeight = 1.5
  backgroundColor = '#F5F5F5'
  gridLineWidth = 0.2

  # Create figure and set the color.
  matplotlib.rc('axes', facecolor=backgroundColor)
  fig = plt.figure(figsize=(windowWidth, windowHeight), 
      facecolor=backgroundColor, dpi=80)
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
    legendPosition = 0
    legendBegin = nextBar
    
    for i, data in enumerate(result):
      # Use this variable to indicate if we have to store the bar handler.
      check = 0

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

      # We can only plot scalar values so we job over the other.
      if time == "failure":
        failure += 1
        continue
      elif str(time).count(">") > 0:
        timeouts += 1
        continue      

      totalTime += time

      # Use the same color for the same dataset and save the timing to find 
      # out the best time.
      if dataset in color:
        barColor = color[dataset]

        # Use the time only if its lower then the old time value.
        timming, lib = bestTiming[dataset]
        if timming > time:
          bestTiming[dataset] = (time, libraries[l])
      else:
        check = 1
        barColor = colors[i%len(colors)]
        color[dataset] = barColor
        legendNames.append(dataset)

        bestTiming[dataset] = (time, libraries[l])

      # Plot the bar chart.
      handler = plt.bar(nextBar, time, barWidth, alpha=opacity, color=barColor, 
          label=dataset, fill=fill, lw=0.2)

      # Increase the width for the next bar.
      nextBar += barWidth
      legendPosition += barWidth

      # Save the bar handler for the legend.
      if check == 1:
        chartHandler.append(handler)

    # Set the right lable postion in the legend.
    legendIndex.append(legendBegin + (legendPosition / 2))
    nextBar += (barWidth * 2)

    # Next library for the next round.
    l += 1

  # Set the labels for the x-axis.
  plt.xticks(legendIndex , libraries)

  # Set the color and the font of the x-axis and y-axis labels.
  ax.tick_params(axis='both', which='major', labelsize=8, labelcolor="#6e6e6e")
  ax.tick_params(axis='both', which='minor', labelsize=6, labelcolor="#6e6e6e")

  # Create the legend under the bar chart.
  lgd = ax.legend(chartHandler, legendNames, loc='upper center', 
    bbox_to_anchor=(0.5, 1.2), fancybox=True, shadow=False, ncol=8, fontsize=8)
  lgd.get_frame().set_linewidth(0)
  for label in lgd.get_texts():
    label.set_color("#6e6e6e")

  # Save the bar chart.
  fig.savefig(fileName, bbox_extra_artists=(lgd,), bbox_inches='tight', 
    facecolor=fig.get_facecolor(), edgecolor='none', format='png')
  plt.close()

  # Count the time in which bestlib is the best.
  bestLibCount = 0
  for dataset, data in bestTiming.items():
    if data[1] == bestlib:
      bestLibCount += 1
  
  return (len(color), totalTime, failure, timeouts, bestLibCount, timingData)

'''
Generate a line chart with the specified informations.

@param data - List which contains the values for the line chart.
@param fileName - The filename of the line chart.
'''
def GenerateSingleLineChart(data, fileName):
  # Bar chart settings.
  lineWidth = 1.5
  opacity = 0.9
  windowWidth = 11
  windowHeight = 1.5
  backgroundColor = '#F5F5F5'
  gridLineWidth = 0.2

  # Create figure and set the color.
  matplotlib.rc('axes', facecolor=backgroundColor)
  fig = plt.figure(figsize=(windowWidth, windowHeight), 
      facecolor=backgroundColor, dpi=80)
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

  # If we have only have a single value we don't want to start from zero so we 
  # double the data.
  if len(data) == 1:
    data += data
    
  # Create the data for the x-axis.
  X = np.arange(len(data))  

  # Plot the line chart.
  plt.plot(X, data, color=colors[0], alpha=opacity)

  # Set the color and the font of the x-axis and y-axis labels.
  ax.tick_params(axis='both', which='major', labelsize=8, labelcolor="#6e6e6e")
  ax.tick_params(axis='both', which='minor', labelsize=6, labelcolor="#6e6e6e")

  # Save the line chart.
  fig.savefig(fileName, bbox_inches='tight', facecolor=fig.get_facecolor(), 
      edgecolor='none')
  plt.close()
