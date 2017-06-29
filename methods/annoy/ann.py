'''
  @file ann.py

  Class to benchmark the Annoy Approximate Nearest Neighbors method.
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
from misc import *

import numpy as np
from annoy import AnnoyIndex

'''
This class implements the Approximate K-Nearest-Neighbors benchmark.
'''
class ANN(object):

  '''
  Create the Approximate K-Nearest-Neighbors benchmark instance.

  @param dataset - Input dataset to perform Approximate K-Nearest-Neighbors on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
  '''
  Use the Annoy libary to implement Approximate Nearest-Neighbors.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def AnnAnnoy(self, options):
    def RunAnnAnnoy(q):
      totalTimer = Timer()

      # Load input dataset.
      Log.Info("Loading dataset", self.verbose)
      referenceData = np.genfromtxt(self.dataset[0], delimiter=',')
      queryData = np.genfromtxt(self.dataset[1], delimiter=',')
      train, label = SplitTrainData(self.dataset)

      # Parse options.
      if not "k" in options:
        Log.Fatal("Required option: Number of furthest neighbors to find.")
        q.put(-1)
        return -1
      else:
        k = int(options.pop("k"))
        if (k < 1 or k > referenceData.shape[0]):
          Log.Fatal("Invalid k: " + k.group(1) + "; must be greater than 0"
              + " and less or equal than " + str(referenceData.shape[0]))
          q.put(-1)
          return -1
      if not "num_trees" in options:
        Log.Fatal("Required option: Number of trees to build")
        q.put(-1)
        return -1
      else:
        n = int(options.pop("num_trees"))

      if len(options) > 0:
        Log.Fatal("Unknown parameters: " + str(options))
        raise Exception("unknown parameters")

      with totalTimer:
        # Get all the parameters.
        try:
          # Perform Approximate Nearest-Neighbors
          acc = 0
          t = AnnoyIndex(train.shape[1])
          for i in range(len(train)):
              t.add_item(i,train[i])
          t.build(n)
          for i in range(len(queryData)):
              v = t.get_nns_by_vector(queryData[i],k)
        except Exception as e:
          Log.Info(e)
          q.put(e)
          return -1
      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunAnnAnnoy, self.timeout)

  '''
  Perform All K-Nearest-Neighbors. If the method has been successfully completed
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform Approximate Nearest Neighbours.", self.verbose)
    results = None
    if len(self.dataset) >= 2:
      results = self.AnnAnnoy(options)

    if results < 0:
      return results

    return {'Runtime' : results}
