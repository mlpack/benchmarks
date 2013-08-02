'''
  @file graph.py
  @author Marcus Edel

  FUnctions to plot graphs.
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
import matplotlib.pyplot as plt


# Use this colors to plot the graph.
colors = ['#3366CC', '#DC3912', '#FF9900', '#FFFF32', '#109618', '#990099', 
          '#DD4477', '#AAAA11', '#22AA99']

'''
Generate a bar chart with the specified informations.

Data structure: list( list ) = [ [] ]

@param header - Contains the names for the x-axis.
@param data - Contains the values for the chart.
@param chartName - Contains the name for the chart.
'''
def GenerateBarChart(header, data, chartName):
  # Bar chart settings.
  barWidth = 0.25
  opacity = 0.8
  fill = True
  windowWidth = 12
  windowHeight = 8
  backgroundColor = '#F5F5F5'

  # Create figure and set the color.
  matplotlib.rc('axes', facecolor=backgroundColor)
  fig = plt.figure(figsize=(windowWidth, windowHeight), 
      facecolor=backgroundColor)
  ax = plt.subplot(1,1,1)

  # Bar and legend position.
  barIndex = np.arange(len(header)) * 2
  legendIndex = barIndex  

  for i, values in enumerate(data):
    dataset = values[0] # Dataset name.

    # Convert values to float.
    values = values[1:]
    values = [float(x) if isFloat(x) else 0 for x in values]

    # Get the bar chart position for the dataset.
    barIndex = [barIndex[j] + barWidth if x != 0 and i != 0 else barIndex[j] 
        for j, x in enumerate(values)]

    # Plot the bar chart with the defined setting.
    foo = plt.bar(barIndex, values, barWidth, alpha=opacity, 
        color=colors[i%len(colors)], label=dataset, fill=fill, lw=0.2)

    # Get the position for the x-axis legend.
    legendIndex = [legendIndex[j]+(0.5*barWidth) if x != 0 else legendIndex[j] 
        for j, x in enumerate(values)]
    
  # Set the labels for the y-axis.
  plt.ylabel('Seconds (lower is better)')

  # Set the titel for the bar chart.
  plt.title(chartName)

  # Set the labels for the x-axis.
  plt.xticks(legendIndex , header)

  # Create the legend under the bar chart.
  lgd = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), 
      fancybox=True, shadow=True, ncol=8)

  # Save the bar chart.
  fig.savefig(chartName, bbox_extra_artists=(lgd,), bbox_inches='tight', 
      facecolor=fig.get_facecolor(), edgecolor='none')

'''
Generate a line chart with the specified informations.

Data structure: dict( dict( list ) ) = { { [] } }

@param data - Contains the values for the chart.
@param chartName - Contains the name for the chart.
'''
def GenerateLineChart(data, chartName):
  # Bar chart settings.
  lineWidth = 2
  opacity = 0.8
  windowWidth = 12
  windowHeight = 8
  backgroundColor = '#F5F5F5'

  # Create figure and set the color.
  matplotlib.rc('axes', facecolor=backgroundColor)
  fig = plt.figure(figsize=(windowWidth, windowHeight), 
      facecolor=backgroundColor)
  plt.rc('lines', linewidth=lineWidth)
  ax = plt.subplot(1,1,1)

  # Data structure to temporary save the the correct color and the chart handler.
  colorTemp = {}
  legendChartHandler = []
  legendName = []

  i = 0
  for libaryName, timeSeries in data.items():
    for name in timeSeries:
      value = timeSeries[name]  # Timing data.
      value = sorted(value, key=lambda tup: tup[0]) # Sort the timing data.

      # Normalize the timing data and generate the corresponding Z values.
      Y = [float(x[1]) if isFloat(x[1]) else 0 for x in value] 
      X = np.arange(len(Y))

      # Check if the graph has a specified color.
      if name in colorTemp:
        # Plot the line chrt.
        plt.plot(X, Y, color=colorTemp[name], label=name, alpha=opacity)
      else:
        # Save the color to use it later for a graph with the same name.
        color = colors[i%len(colors)]
        # Save the bar handler to generate the legend.
        handler, = plt.plot(X, Y, color=color, label=name, alpha=opacity)
        colorTemp[name] = color
        legendChartHandler.append(handler)
        legendName.append(name)
      i += 1

  # Set the labels for the y-axis.
  plt.ylabel('Seconds (lower is better)')

  # Set the titel for the bar chart.
  plt.title(chartName)

  # Create the legend under the bar chart.
  lgd = plt.legend(legendChartHandler, legendName, loc='upper center', 
      bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=8)  

  # Save the line chart.
  fig.savefig(chartName, bbox_extra_artists=(lgd,), bbox_inches='tight', 
      facecolor=fig.get_facecolor(), edgecolor='none')
