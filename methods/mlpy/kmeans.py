'''
  @file kmeans.py
  @author Marcus Edel

  K-Means Clustering with mlpy.
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

import numpy as np
import mlpy

'''
This class implements the K-Means Clustering benchmark.
'''
class KMEANS(object):

  '''
  Create the K-Means Clustering benchmark instance.

  @param dataset - Input dataset to perform K-Means on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout

  '''
  Use the mlpy libary to implement K-Means Clustering.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def KMeansMlpy(self, options):
    def RunKMeansMlpy(q):
      totalTimer = Timer()

      # Load input dataset.
      Log.Info("Loading dataset", self.verbose)
      data = np.genfromtxt(self.dataset[0], delimiter=',')

      # Gather all parameters.
      if "clusters" in options:
        clusters = int(options.pop("clusters"))

        if clusters < 1:
          Log.Fatal("Invalid number of clusters requested! Must be greater than or "
              + "equal to 1.")
          q.put(-1)
          return -1
      else:
        Log.Fatal("Required option: Number of clusters or cluster locations.")
        q.put(-1)
        return -1

      build_opts = {}
      if "seed" in options:
        build_opts["seed"] = int(options.pop("seed"))

      if len(options) > 0:
        Log.Fatal("Unknown parameters: " + str(options))
        raise Exception("unknown parameters")

      try:
        with totalTimer:
          # Create the K-Means object and perform K-Means clustering.
          kmeans = mlpy.kmeans(data, clusters, **build_opts)
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunKMeansMlpy, self.timeout)

  '''
  Perform K-Means Clustering. If the method has been successfully completed
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform K-Means.", self.verbose)

    results = self.KMeansMlpy(options)
    if results < 0:
      return results

    return {'Runtime' : results}
