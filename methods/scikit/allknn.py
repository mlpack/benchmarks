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
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def AllKnnScikit(self, options):
    def RunAllKnnScikit(q):
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
        build_opts = {}
        if "k" in options:
          build_opts["n_neighbors"] = int(options.pop("k"))
          if (build_opts["n_neighbors"] < 1 or build_opts["n_neighbors"] > referenceData.shape[0]):
            Log.Fatal("Invalid k: " + str(build_opts["n_neighbors"]) + "; must be greater than 0"
              + " and less or equal than " + str(referenceData.shape[0]))
            q.put(-1)
            return -1
        else:
          Log.Fatal("Required option: Number of furthest neighbors to find.")
          q.put(-1)
          return -1

        if "leaf_size" in options:
          build_opts["leaf_size"] = int(options.pop("leaf_size"))
          if build_opts["leaf_size"] < 0:
            Log.Fatal("Invalid leaf size: " + str(build_opts["leaf_size"]) + ". Must" +
                " be greater than or equal to 0.")
          q.put(-1)
          return -1
        else:
          build_opts["leaf_size"] = 20

        if "tree_type" in options:
          build_opts["tree_type"] = str(options.pop("tree_type"))
          if build_opts["tree_type"] != 'auto' or \
             build_opts["tree_type"] != 'ball_tree' or \
             build_opts["tree_type"] != 'kd_tree' or \
             build_opts["tree_type"] != 'brute':
            Log.Fatal("Invalid tree type: "+ build_opts["tree_type"]
                + ". Must be either auto, ball_tree, kd_tree or brute.")
            q.put(-1)
            return -1

        if "radius" in options:
          build_opts["radius"] = float(options.pop("radius"))
        if "metric" in options:
          build_opts["metric"] = str(options.pop("metric"))
          if build_opts["metric"] not in ['cityblock', 'cosine', 'euclidean', 'l1', 'l2', 'manhattan']:
            Log.Fatal("Invalid metric type: "+ build_opts["metric"]
                + ". Must be either cityblock, cosine, euclidean, l1, l2 or manhattan")
            q.put(-1)
            return -1
          if "p" in options:
            build_opts["p"] = int(options.pop("p"))

        if "num_jobs" in options:
          build_opts["n_jobs"] = int(options.pop("num_jobs"))

        if len(options) > 0:
          Log.Fatal("Unknown parameters: " + str(options))
          raise Exception("unknown parameters")

        try:
          # Perform All K-Nearest-Neighbors.
          model = NearestNeighbors(**build_opts)
          model.fit(referenceData)

          if len(self.dataset) == 2:
            out = model.kneighbors(queryData, build_opts["n_neighbors"], return_distance=True)
          else:
            # We have to increment k by one because mlpack ignores the
            # self-neighbor, whereas scikit-learn will happily return the
            # nearest neighbor of point 0 as point 0.
            out = model.kneighbors(referenceData, build_opts["n_neighbors"] + 1, return_distance=True)
        except Exception as e:
          q.put(-1)
          return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunAllKnnScikit, self.timeout)

  '''
  Perform All K-Nearest-Neighbors. If the method has been successfully completed
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform ALLKNN.", self.verbose)

    results = self.AllKnnScikit(options)
    if results < 0:
      return results

    return {'Runtime' : results}
