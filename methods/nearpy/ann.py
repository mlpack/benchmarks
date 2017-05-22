'''
  @file ann.py

  Class to benchmark the Nearpy Approximate Nearest Neighbors method.
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
from nearpy import Engine
from nearpy.hashes import RandomBinaryProjections

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
  Use the Nearpy libary to implement Approximate Nearest-Neighbors.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def AnnNearpy(self, options):
    def RunAnnNearpy(q):
      totalTimer = Timer()

      # Load input dataset.
      Log.Info("Loading dataset", self.verbose)
      queryData = np.genfromtxt(self.dataset[1], delimiter=',')
      train, label = SplitTrainData(self.dataset)

      with totalTimer:
        # Get all the parameters.
        try:
          # Perform Approximate Nearest-Neighbors
          dimension = train.shape[1]
          rbp = RandomBinaryProjections('rbp', 10)
          engine = Engine(dimension, lshashes=[rbp])
          for i in range(len(train)):
              engine.store_vector(train[i],'data_%d' % i)
          for i in range(len(queryData)):
              v = engine.neighbours(queryData[i])
        except Exception as e:
          Log.Info(e)
          q.put(e)
          return -1
      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunAnnNearpy, self.timeout)

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
    if len(self.dataset)>=2:
      results = self.AnnNearpy(options)

    if results < 0:
      return results

    return {'Runtime' : results}
