'''
  @file kmeans.py
  @author Marcus Edel

  K-Means Clustering with shogun.
'''

import os
import sys
import inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from log import *
from timer import *

import shlex
import subprocess
import re
import collections

'''
This class implements the K-Means Clustering benchmark.
'''
class KMEANS(object):

  ''' 
  Create the K-Means Clustering benchmark instance.
  
  @param dataset - Input dataset to perform K-Means Clustering on.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, verbose=True): 
    self.verbose = verbose
    self.dataset = dataset

  '''
  Destructor to clean up at the end.
  '''
  def __del__(self):
    pass

  '''
  Use the shogun libary to implement K-Means Clustering.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def KMeansShogun(self, options):
    totalTimer = Timer()

    # Gather parameters.
    clusters = re.search("-c (\d+)", options)
    seed = re.search("-s (\d+)", options)
    maxIterations = re.search("-m (\d+)", options)

    # Now do validation of options.
    if not clusters and len(self.dataset) != 2:
      Log.Fatal("Required option: Number of clusters or cluster locations.")
      return -1
    elif (not clusters or clusters.group(1) < 1):
      Log.Fatal("Invalid number of clusters requested! Must be greater than or "
          + "equal to 1.")
      return -1

    maxIterations = 1000 if not maxIterations else int(maxIterations.group(1))

    # Load input dataset.
    # If the dataset contains two files then the second file is the centroids 
    # file. In this case we run the the kmeans executable.
    Log.Info("Loading dataset", self.verbose)
    if len(self.dataset) == 2:

      # Run command with the nessecary arguments and return its output as a byte 
      # string. We have untrusted input so we disables all shell based features.
      cmd = shlex.split("methods/shogun/kmeans " + self.dataset[0] 
          + " " + self.dataset[1] + " " + clusters.group(1) + " " 
          + str(maxIterations))
      try:
        s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False) 
      except Exception, e:
        Log.Fatal("Could not execute command: " + str(cmd))
        return -1

      # Return the elapsed time.
      timer = self.parseTimer(s)
      if not timer:
        Log.Fatal("Can't parse the timer")
        return -1
      else:
        time = self.GetTime(timer)
        Log.Info(("total time: %fs" % (time)), self.verbose)

        return time      

    else:
      import numpy as np
      from shogun.Distance import EuclideanDistance
      from shogun.Features import RealFeatures
      from shogun import Clustering
      from shogun.Mathematics import Math_init_random

      if seed:
        Math_init_random(seed.group(1))

      data = np.genfromtxt(self.dataset, delimiter=',')

      dataFeat = RealFeatures(data.T)
      distance = EuclideanDistance(dataFeat, dataFeat)

      # Create the K-Means object and perform K-Means clustering.
      with totalTimer:
        model = Clustering.KMeans(int(clusters.group(1)), distance)
        model.set_max_iter(maxIterations)
        model.train()

        labels = model.apply().get_labels()
        centers = model.get_cluster_centers()

      return totalTimer.ElapsedTime()

  '''
  Perform K-Means Clustering. If the method has been successfully 
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def RunMethod(self, options):
    Log.Info("Perform K-Means.", self.verbose)

    return self.KMeansShogun(options)

  '''
  Parse the timer data form a given string.

  @param data - String to parse timer data from.
  @return - Namedtuple that contains the timer data.
  '''
  def parseTimer(self, data):
    # Compile the regular expression pattern into a regular expression object to
    # parse the timer data.
    pattern = re.compile(r"""
        .*?total_time: (?P<total_time>.*?)s.*?
        """, re.VERBOSE|re.MULTILINE|re.DOTALL)
    
    match = pattern.match(data)
    if not match:
      Log.Fatal("Can't parse the data: wrong format")
      return -1
    else:
      # Create a namedtuple and return the timer data.
      timer = collections.namedtuple("timer", ["total_time"])
      
      return timer(float(match.group("total_time")))

  '''
  Return the elapsed time in seconds.

  @param timer - Namedtuple that contains the timer data.
  @return Elapsed time in seconds.
  '''
  def GetTime(self, timer):
    time = timer.total_time
    return time
