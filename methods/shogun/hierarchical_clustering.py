'''
  @file hierarchical_clustering.py
  @author Chirag Pabbaraju

  Hierarchical CLustering with shogun.
'''

import sys
import os
import inspect
import timeout_decorator
import numpy as np

# Import the util path, this method even works if the path contains symlinks to modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from log import *
from timer import *

from modshogun import Hierarchical, EuclideanDistance, RealFeatures

'''
This class implements the Hierarchical Clustering benchmark.
'''
class HierarchicalClustering(object):

  '''
  Create the Hierarchical Clustering benchmark instance.
  
    @param dataset - Input dataset to perform Hierarchical Clustering on.
    @param timeout - The time until the timeout. Default no timeout.
    @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout

  '''
    Use the shogun libary to implement Hierarchical Clustering.
    @param options - Options for the model
    @return - Elapsed time in seconds or a negative value if the method was not successful. 

  '''
  def HierarchicalShogun(self, options):
    @timeout_decorator.timeout(self.timeout)
    def RunHierarchicalShogun():
      totalTimer = Timer()

      try:
        # Load input dataset.
        Log.Info("Loading dataset", self.verbose)
        dataPoints = np.genfromtxt(self.dataset, delimiter=',')
        dataFeat = RealFeatures(dataPoints.T)
        distance = EuclideanDistance(dataFeat, dataFeat)

        # Gather all the parameters.
        if "merges" in options:
          merges = int(options.pop("merges"))
        else:
          Log.Fatal("Missing parameter: number of merges to be done while clustering bottom up")
          raise Exception("missing parameter")

        if(len(options) > 0):
          Log.Fatal("Unknown options: " + str(options))
          raise Exception("unknown options")

        # Create the Hierarchical object and perform Hierarchical clustering.
        with totalTimer:
          model = Hierarchical(merges, distance)
          model.train()

        merge_distances = model.get_merge_distances()
        cluster_pairs = model.get_cluster_pairs()

      except Exception as e:
        Log.Info("Exception: " + str(e))
        return -1

      return totalTimer.ElapsedTime()

    try:
      return RunHierarchicalShogun()
    except timeout_decorator.TimeoutError:
      Log.Info("Timeout error")
      return -1

  '''
    Perform Hierarchical clustering. If the method has been successfully completed return the elapsed time in seconds.

    @param options - Extra options for the method.
    @return - Elapsed time in seconds or a negative value if the method was not successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform Hierarchical clustering.", self.verbose)
    results = self.HierarchicalShogun(options)
    if results < 0:
      return results

    return {"Runtime" : results}
