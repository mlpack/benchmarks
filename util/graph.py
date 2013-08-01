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

'''
Generate a bar chart with the specified informations.

@param header - Contains the names for the x-axis.
@param data - Contains the values for the chart.
@param name - Contains the name for the chart.
'''
def GenerateBarChart(header, data, name):
  # Bar chart settings.
  colors = ['#3366CC', '#DC3912', '#FF9900', '#FFFF32', '#109618', '#990099', '#DD4477']
  barWidth = 0.25
  opacity = 0.8
  fill = True
  windowWidth = 12
  windowHeight = 8
  backgroundColor = '#F5F5F5'

  # Create figure and set the color.
  matplotlib.rc('axes', facecolor=backgroundColor)
  fig = plt.figure(figsize=(windowWidth, windowHeight), facecolor=backgroundColor)
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
    barIndex = [barIndex[j] + barWidth if x != 0 and i != 0 else barIndex[j] for j, x in enumerate(values)]

    # Plot the bar chart with the defined setting.
    foo = plt.bar(barIndex, values, barWidth, alpha=opacity, color=colors[i%len(colors)], label=dataset, fill=fill, lw=0.2)

    # Get the position for the x-axis legend.
    legendIndex = [legendIndex[j]+(0.5*barWidth) if x != 0 else legendIndex[j] for j, x in enumerate(values)]
    
  # Set the labels for the y-axis.
  plt.ylabel('Seconds (lower is better)')

  # Set the titel for the bar chart.
  plt.title(name)

  # Set the labels for the x-axis.
  plt.xticks(legendIndex , header)

  # Create the legend under the bar chart.
  lgd = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=8)

  # Save the bar chart.
  fig.savefig(name, bbox_extra_artists=(lgd,), bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')

  plt.show()
