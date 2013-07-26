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
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def KMeansScikit(self, options):

    @timeout(self.timeout, os.strerror(errno.ETIMEDOUT))
    def RunKMeansScikit():
      totalTimer = Timer()

      # Load input dataset.
      # If the dataset contains two files then the second file is the centroids 
      # file. In this case we add this to the command line.
      Log.Info("Loading dataset", self.verbose)
      if len(self.dataset) == 2:
        data = np.genfromtxt(self.dataset[0], delimiter=',')
        centroids = np.genfromtxt(self.dataset[1], delimiter=',')
      else:
        data = np.genfromtxt(self.dataset, delimiter=',')

      # Gather parameters.
      clusters = re.search("-c (\d+)", options)
      maxIterations = re.search("-m (\d+)", options)
      seed = re.search("-s (\d+)", options)

      # Now do validation of options.
      if not clusters and len(self.dataset) != 2:
        Log.Fatal("Required option: Number of clusters or cluster locations.")
        return -1
      elif (not clusters or int(clusters.group(1)) < 1) and len(self.dataset) != 2:
        Log.Fatal("Invalid number of clusters requested! Must be greater than or "
            + "equal to 1.")
        return -1

      m = 1000 if not maxIterations else int(maxIterations.group(1))

      # Create the KMeans object and perform K-Means clustering.
      with totalTimer:
        if len(self.dataset) == 2:
          kmeans = KMeans(k=centroids.shape[1], init=centroids, n_init=1, 
              max_iter=m)
        elif seed:
          kmeans = KMeans(n_clusters=int(clusters.group(1)), init='random', 
              n_init=1, max_iter=m, random_state=int(seed.group(1)))
        else:
          kmeans = KMeans(n_clusters=int(clusters.group(1)), n_init=1, max_iter=m)      

        kmeans.fit(data)
        labels = kmeans.labels_
        centers = kmeans.cluster_centers_

      return totalTimer.ElapsedTime()

    try:
      return RunKMeansScikit()
    except TimeoutError as e:
      Log.Warn("Script timed out after " + str(self.timeout) + " seconds")
      return -2

  '''
  Perform K-Means Clustering. If the method has been successfully completed 
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def RunMethod(self, options):
    Log.Info("Perform K-Means.", self.verbose)

    return self.KMeansScikit(options)
