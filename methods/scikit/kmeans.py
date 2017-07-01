'''
  @file kmeans.py
  @author Marcus Edel

  K-Means Clustering with scikit.
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
from sklearn.cluster import KMeans

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
  Use the scikit libary to implement K-Means Clustering.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def KMeansScikit(self, options):
    def RunKMeansScikit(q):
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
      opts = {}
      if "clusters" in options:
        opts["n_clusters"] = int(options.pop("clusters"))
      elif len(self.dataset) != 2:
        Log.Fatal("Required option: Number of clusters or cluster locations.")
        q.put(-1)
        return -1
      if "max_iterations" in options:
        opts["max_iterations"] = int(options.pop("max_iterations"))
      if "seed" in options:
        opts["random_state"] = int(options.pop("seed"))
        opts["init"] = "random"
      if "algorithm" in options:
        opts["algorithm"] = str(options.pop("algorithm"))
        if "algorithm" not in ['naive', 'elkan', 'auto']:
          Log.Fatal("Invalid value for algorithm: "+algorithm+" must be either elkan or naive")
          q.put(-1)
          return -1

      if len(options) > 0:
        Log.Fatal("Unknown parameters: " + str(options))
        raise Exception("unknown parameters")

      try:
        # Create the KMeans object and perform K-Means clustering.
        with totalTimer:
          if len(self.dataset) == 2:
            opts["init"] = centroids
          kmeans = KMeans(**opts)
          kmeans.fit(data)
          labels = kmeans.labels_
          centers = kmeans.cluster_centers_
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunKMeansScikit, self.timeout)

  '''
  Perform K-Means Clustering. If the method has been successfully completed
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform K-Means.", self.verbose)

    results = self.KMeansScikit(options)
    if results < 0:
      return results

    return {'Runtime' : results}
