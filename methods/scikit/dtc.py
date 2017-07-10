'''
  @file dtc.py
  @author Marcus Edel

  Decision Tree Classifier with scikit.
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

import numpy as np
from sklearn.tree import DecisionTreeClassifier

'''
This class implements the Decision Tree Classifier benchmark.
'''
class DTC(object):

  '''
  Create the Decision Tree Classifier benchmark instance.

  @param dataset - Input dataset to perform DTC on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.model = None
    self.predictions = None
    self.build_opts = {}
  '''
  Build the model for the Decision Tree Classifier.

  @param data - The train data.
  @param labels - The labels for the train set.
  @return The created model.
  '''
  def BuildModel(self, data, labels):
    # Create and train the classifier.
    dtc = DecisionTreeClassifier(**self.build_opts)
    dtc.fit(data, labels)
    return dtc

  '''
  Use the scikit libary to implement the Decision Tree Classifier.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def DTCScikit(self, options):
    def RunDTCScikit(q):
      totalTimer = Timer()

      Log.Info("Loading dataset", self.verbose)
      trainData, labels = SplitTrainData(self.dataset)
      testData = LoadDataset(self.dataset[1])

      # Get all the parameters.
      self.build_opts = {}
      if "fitness_function" in options:
        self.build_opts["criterion"] = str(options.pop("criterion"))
      if "max_depth" in options:
        self.build_opts["max_depth"] = int(options.pop("max_depth"))
      if "split_strategy" in options:
        self.build_opts["splitter"] = str(options.pop("split_strategy"))
      if "minimum_samples_split" in options:
        self.build_opts["min_samples_split"] = \
            int(options.pop("minimum_samples_split"))
      if "minimum_leaf_size" in options:
        self.build_opts["min_samples_leaf"] = int(options.pop("minimum_leaf_size"))
      if "max_features" in options:
        self.build_opts["max_features"] = int(options.pop("max_features"))
      if "max_leaf_nodes" in options:
        self.build_opts["max_leaf_nodes"] = int(options.pop("max_leaf_nodes"))
      if "seed" in options:
        self.build_opts["random_state"] = int(options.pop("seed"))

      if len(options) > 0:
        Log.Fatal("Unknown parameters: " + str(options))
        raise Exception('unknown parameters')

      try:
        with totalTimer:
          self.model = self.BuildModel(trainData, labels)
          # Run Decision Tree Classifier on the test dataset.
          self.predictions = self.model.predict(testData)
      except Exception as e:
        Log.Debug(str(e))
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put((time, self.predictions))

      return time

    result = timeout(RunDTCScikit, self.timeout)
    # Check for error, in this case the tuple doesn't contain extra information.
    if len(result) > 1:
       self.predictions = result[1]

    return result[0]

  '''
  Perform the Decision Tree Classifier. If the method has been
  successfully completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform DTC.", self.verbose)

    results = None
    if len(self.dataset) >= 2:
      results = self.DTCScikit(options)

      if results < 0:
        return results
    else:
      Log.Fatal("This method requires two datasets.")

    # Datastructure to store the results.
    metrics = {'Runtime' : results}

    if len(self.dataset) >= 3:
      # Check if we need to create a model.
      truelabels = LoadDataset(self.dataset[2])

      confusionMatrix = Metrics.ConfusionMatrix(truelabels, self.predictions)
      metrics['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metrics['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metrics['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metrics['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metrics['MSE'] = Metrics.SimpleMeanSquaredError(truelabels, self.predictions)

    return metrics

