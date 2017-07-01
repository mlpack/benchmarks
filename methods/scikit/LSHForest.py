'''
  @file LSHForest.py

  Approximate Nearest Neighbors using LSHForest with scikit.
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

#Import the metrics definitions path.
metrics_folder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../metrics")))
if metrics_folder not in sys.path:
  sys.path.insert(0, metrics_folder)

from log import *
from timer import *
from definitions import *
from misc import *

from sklearn.neighbors import LSHForest

'''
This class implements the Approximate Nearest Neighbors benchmark.
'''
class ANN(object):

  '''
  Create the Approximate Nearest Neighbors benchmark instance.

  @param dataset - Input dataset to perform ANN on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.model = None
    self.build_opts = {}

  '''
  Build the model for the Approximate Nearest Neighbors.

  @param data - The train data.
  @param labels - The labels for the train set.
  @return The created model.
  '''
  def BuildModel(self, data, labels):
    # Create and train the classifier.
    lshf = LSHForest(**self.build_opts)
    lshf.fit(data)
    return lshf

  '''
  Use the scikit libary to implement Approximate Nearest Neighbors.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def AnnScikit(self, options):
    def RunAnnScikit(q):
      totalTimer = Timer()

      Log.Info("Loading dataset", self.verbose)
      trainData, labels = SplitTrainData(self.dataset)
      testData = LoadDataset(self.dataset[1])
      # Number of trees in the LSH Forest.
      self.build_opts = {}
      if "num_trees" in options:
        self.build_opts["n_estimators"] = int(options.pop("num_trees"))
      # Number of neighbors to be returned from the query function.
      if "k" in options:
        n_neighbors = int(options.pop("k"))
      else:
        Log.Fatal("Required parameter 'k' not specified!")
        raise Exception("missing parameter")
      # Lowest hash length to be searched when candidate selection is performed.
      if "min_hash_match" in options:
        self.build_opts["min_hash_match"] = int(options.pop("min_hash_match"))
      # Minimum number of candidates evaluated per estimator.
      if "num_candidates" in options:
        self.build_options["n_candidates"] = int(options.pop("n_candidates"))
      # Radius from data point to its neighbors.
      if "radius" in options:
        self.build_options["radius"] = float(options.pop("radius"))
      # A value ranges from 0 to 1.
      if "radius_cutoff_ratio" in options:
        self.build_options["radius_cutoff_ratio"] = \
            float(options.pop("radius_cutoff_ratio"))

      if len(options) > 0:
        Log.Fatal("Unknown parameters: " + str(options))
        raise Exception("unknown parameters")

      try:
        with totalTimer:
          self.model = self.BuildModel(trainData, labels)
          # Run Approximate on the test dataset.
          distances,indices = self.model.kneighbors(testData,
                                                    n_neighbors=n_neighbors)
      except Exception as e:
        Log.Debug(str(e))
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)

      return time

    return timeout(RunAnnScikit, self.timeout)

  '''
  Perform Approximate Nearest Neighbors. If the method has been successfully
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform ANN.", self.verbose)

    results = None
    if len(self.dataset) >= 2:
      results = self.AnnScikit(options)

      if results < 0:
        return results
    else:
      Log.Fatal("This method requires two datasets.")

    # Datastructure to store the results.
    metrics = {'Runtime' : results}
    
    return metrics

