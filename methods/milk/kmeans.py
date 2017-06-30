'''
  @file kmeans.py

  K-Means Clustering with milk.
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
from milk import kmeans

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
  Use the Milk libary to implement K-Means Clustering.
  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def KMeansMilk(self, options):
    def RunKMeansMilk(q):
      totalTimer = Timer()

      # Load input dataset.
      # If the dataset contains two files then the second file is the centroids
      # file.
      Log.Info("Loading dataset", self.verbose)
      if len(self.dataset) == 2:
        data = np.genfromtxt(self.dataset[0], delimiter=',')
        centroids = np.genfromtxt(self.dataset[1], delimiter=',')
      else:
        data = np.genfromtxt(self.dataset, delimiter=',')

      # Gather parameters.
      clusters = None
      if "clusters" in options:
        clusters = options.pop("clusters")
      maxIterations = None
      if "max_iterations" in options:
        maxIterations = options.pop("max_iterations")
      if len(options) > 0:
        Log.Fatal("Unknown parameters: " + str(options))
        raise Exception("unknown parameters")

      # Now do validation of options.
      if not clusters and len(self.dataset) != 2:
        Log.Fatal("Required option: Number of clusters or cluster locations.")
        q.put(-1)
        return -1
      elif (not clusters or int(clusters) < 1) and len(self.dataset) != 2:
        Log.Fatal("Invalid number of clusters requested! Must be greater than"
            + " or equal to 1.")
        q.put(-1)
        return -1

      m = 1000 if not maxIterations else int(maxIterations)

      try:
        # Create the KMeans object and perform K-Means clustering.
        with totalTimer:
          if len(self.dataset) == 2:
            assignments = kmeans(data,
                                 int(clusters),
                                 max_iter=m,
                                 centroids=centroids,
                                 return_centroids=False)
          else:
            assignments, centroids = kmeans(data,
                                            int(clusters),
                                            max_iter=m)

      except Exception as e:
        Log.Fatal("Exception: " + str(e))
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunKMeansMilk, self.timeout)

  '''
  Perform K-Means Clustering. If the method has been successfully completed
  return the elapsed time in seconds.
  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform K-Means.", self.verbose)

    results = self.KMeansMilk(options)
    if results < 0:
      return results

    return {'Runtime' : results}
