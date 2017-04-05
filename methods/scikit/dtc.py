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
    self.criterion = 'gini'
    self.max_depth = None
    self.seed = 0
    self.splitter = 'best'
    self.max_depth = None
    self.min_samples_split = 2
    self.min_samples_leaf = 1
    self.min_weight_fraction_leaf = 0.0
    self.max_features = None
    self.random_state = None
    self.min_impurity_split = 1e-07
    self.class_weight = None
    self.presort = False
  '''
  Build the model for the Decision Tree Classifier.

  @param data - The train data.
  @param labels - The labels for the train set.
  @return The created model.
  '''
  def BuildModel(self, data, labels):
    # Create and train the classifier.
    dtc = DecisionTreeClassifier(criterion=self.criterion,
                                 max_depth=self.max_depth,
                                 random_state=self.seed,
                                 splitter = self.splitter,
                                 min_samples_split = self.min_samples_split,                                 
                                 min_weight_fraction_leaf=self.min_weight_fraction_leaf,
                                 max_features = self.max_features,
                                 max_leaf_nodes = self.max_leaf_nodes,
                                 min_impurity_split = self.min_impurity_split,
                                 class_weight = self.class_weight,
                                 presort = self.presort)
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
      c = re.search("-c (\s+)", options)
      d = re.search("-d (\s+)", options)
      s = re.search("-s (\d+)", options)
      mss = re.search("--min_samples_split (\d+)", options)
      msl = re.search("--min_samples_leaf (\d+)", options)
      mf = re.search("--max_features (\d+)", options)
      mln = re.search("--max_leaf_nodes (\d+)", options)
      
      self.criterion = 'gini' if not c else str(c.group(1))
      self.max_depth = None if not d else int(d.group(1))
      self.splitter = 'best' if not s else str(s.group(1))
      self.min_samples_split = 2 if not mss else int(mss.group(1))
      self.min_samples_leaf = 1 if not msl else int(msl.group(1))
      self.max_features = None if not mf else int(mf.group(1))
      self.max_leaf_nodes = None if not mln else int(mln.group(1))
      self.seed = 0 if not s else int(s.group(1))

      try:
        with totalTimer:
          self.model = self.BuildModel(trainData, labels)
          # Run Decision Tree Classifier on the test dataset.
          self.model.predict(testData)
      except Exception as e:
        Log.Debug(str(e))
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)

      return time

    return timeout(RunDTCScikit, self.timeout)

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
      if not self.model:
        trainData, labels = SplitTrainData(self.dataset)
        self.model = self.BuildModel(trainData, labels)

      testData = LoadDataset(self.dataset[1])
      truelabels = LoadDataset(self.dataset[2])
      predictedlabels = self.model.predict(testData)

      confusionMatrix = Metrics.ConfusionMatrix(truelabels, predictedlabels)
      metrics['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metrics['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metrics['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metrics['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metrics['MSE'] = Metrics.SimpleMeanSquaredError(truelabels, predictedlabels)

    return metrics

