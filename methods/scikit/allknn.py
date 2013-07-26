'''
  @file allknn.py
  @author Marcus Edel

  All K-Nearest-Neighbors with scikit.
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
from sklearn.neighbors import NearestNeighbors

'''
This class implements the All K-Nearest-Neighbors benchmark.
'''
class ALLKNN(object):

  ''' 
  Create the All K-Nearest-Neighbors benchmark instance.
  
  @param dataset - Input dataset to perform All K-Nearest-Neighbors on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout

  '''
  Use the scikit libary to implement All K-Nearest-Neighbors.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def AllKnnScikit(self, options):

    @timeout(self.timeout, os.strerror(errno.ETIMEDOUT))
    def RunAllKnnScikit():
      totalTimer = Timer()

      # Load input dataset.
      # If the dataset contains two files then the second file is the query file 
      # In this case we add this to the command line.
      Log.Info("Loading dataset", self.verbose)
      if len(self.dataset) == 2:
        referenceData = np.genfromtxt(self.dataset[0], delimiter=',')
        queryData = np.genfromtxt(self.dataset[1], delimiter=',')
      else:
        referenceData = np.genfromtxt(self.dataset, delimiter=',')

      with totalTimer:
        # Get all the parameters.
        k = re.search("-k (\d+)", options)
        leafSize = re.search("-l (\d+)", options)

        if not k:
          Log.Fatal("Required option: Number of furthest neighbors to find.")
          return -1
        else:
          k = int(k.group(1))
          if (k < 1 or k > referenceData.shape[0]):
            Log.Fatal("Invalid k: " + k.group(1) + "; must be greater than 0 and "
              + "less ")
            return -1

        if not leafSize:
          l = 20
        elif int(leafSize.group(1)) < 0:
          Log.Fatal("Invalid leaf size: " + str(leafSize.group(1)) + ". Must be " +
              "greater than or equal to 0.")
          return -1
        else:
          l = int(leafSize.group(1))

        # Perform All K-Nearest-Neighbors.
        model = NearestNeighbors(n_neighbors=k, algorithm='kd_tree', leaf_size=l)
        model.fit(referenceData)

        if len(self.dataset) == 2:
          out = model.kneighbors(queryData, k, return_distance=True)
        else:
          out = model.kneighbors(referenceData, k, return_distance=True)

      return totalTimer.ElapsedTime()

    try:
      return RunAllKnnScikit()
    except TimeoutError as e:
      Log.Warn("Script timed out after " + str(self.timeout) + " seconds")
      return -2

  '''
  Perform All K-Nearest-Neighbors. If the method has been successfully completed 
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def RunMethod(self, options):
    Log.Info("Perform ALLKNN.", self.verbose)

    return self.AllKnnScikit(options)
