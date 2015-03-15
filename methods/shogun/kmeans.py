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

import numpy as np
from modshogun import EuclideanDistance, RealFeatures, KMeans, Math_init_random

'''
This class implements the K-Means Clustering benchmark.
'''
class KMEANS(object):

  '''
  Create the K-Means Clustering benchmark instance.

  @param dataset - Input dataset to perform K-Means Clustering on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout

  '''
  Use the shogun libary to implement K-Means Clustering.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def KMeansShogun(self, options):
    def RunKMeansShogun(q):
      totalTimer = Timer()

      # Load input dataset.
      # If the dataset contains two files then the second file is the centroids
      # file.
      Log.Info("Loading dataset", self.verbose)
      if len(self.dataset) == 2:
        data = np.genfromtxt(self.dataset[0], delimiter=',')
        centroids = np.genfromtxt(self.dataset[1], delimiter=',')
      else:
        data = np.genfromtxt(self.dataset[0], delimiter=',')

      # Gather parameters.
      clusters = re.search("-c (\d+)", options)
      maxIterations = re.search("-m (\d+)", options)
      seed = re.search("-s (\d+)", options)

      # Now do validation of options.
      if not clusters and len(self.dataset) != 2:
        Log.Fatal("Required option: Number of clusters or cluster locations.")
        q.put(-1)
        return -1
      elif (not clusters or int(clusters.group(1)) < 1) and len(self.dataset) != 2:
        Log.Fatal("Invalid number of clusters requested! Must be greater than"
            + " or equal to 1.")
        q.put(-1)
        return -1

      m = 1000 if not maxIterations else int(maxIterations.group(1))


      if seed:
        Math_init_random(seed.group(1))
      try:
        dataFeat = RealFeatures(data.T)
        distance = EuclideanDistance(dataFeat, dataFeat)

        # Create the K-Means object and perform K-Means clustering.
        with totalTimer:
          if len(self.dataset) == 2:
            model = KMeans(int(clusters.group(1)), distance, RealFeatures(centroids))
          else:
            model = KMeans(int(clusters.group(1)), distance)

          model.set_mbKMeans_iter(m)
          model.train()

          labels = model.apply().get_labels()
          centers = model.get_cluster_centers()
      except Exception as e:
        print(e)
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunKMeansShogun, self.timeout)

  '''
  Perform K-Means Clustering. If the method has been successfully
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunTiming(self, options):
    Log.Info("Perform K-Means.", self.verbose)

    return self.KMeansShogun(options)

  '''
  Parse the timer data form a given string.

  @param data - String to parse timer data from.
  @return - Namedtuple that contains the timer data or -1 in case of an error.
  '''
  def parseTimer(self, data):
    # Compile the regular expression pattern into a regular expression object to
    # parse the timer data.
    pattern = re.compile(br"""
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
    return timer.total_time
