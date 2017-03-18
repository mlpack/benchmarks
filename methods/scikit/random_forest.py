'''
  @file random_forest.py
  @author Marcus Edel

  Random Forest Classifier with scikit.
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
from sklearn.ensemble import RandomForestClassifier

'''
This class implements the Random Forest Classifier benchmark.
'''
class RANDOMFOREST(object):

  '''
  Create the Random Forest Classifier benchmark instance.

  @param dataset - Input dataset to perform RANDOMFOREST on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.model = None
    self.n_estimators = 10
    self.criterion = 'gini'
    self.max_depth = None
    self.seed = 0
    self.min_samples_split = 2
    self.min_samples_leaf = 1
    self.min_weight_fraction_leaf = 0.0
    self.max_features = 'auto'
    self.max_leaf_nodes = None
    self.min_impurity_split = 1e-07
    self.bootstrap = True
    self.oob_score = False
    self.n_jobs = 1
    self.warm_start = False
    self.class_weight = None
  '''
  Build the model for the Random Forest Classifier.

  @param data - The train data.
  @param labels - The labels for the train set.
  @return The created model.
  '''
  def BuildModel(self, data, labels):
    # Create and train the classifier.
    randomforest = RandomForestClassifier(n_estimators=self.n_estimators,
                                          max_depth=self.max_depth,
                                          criterion=self.criterion,
                                          random_state=self.seed,
                                          min_samples_split = self.min_samples_split,
                                          min_samples_leaf = self.min_samples_leaf,
                                          min_weight_fraction_leaf = self.min_weight_fraction_leaf,
                                          max_features = self.max_features,max_leaf_nodes =self.max_leaf_nodes,
                                          min_impurity_split = self.min_impurity_split,bootstrap = self.bootstrap,
                                          oob_score = self.oob_score,n_jobs = self.n_jobs,warm_start = self.warm_start,
                                          class_weight = self.class_weight)
    randomforest.fit(data, labels)
    return randomforest

  '''
  Use the scikit libary to implement the Random Forest Classifier.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RANDOMFORESTScikit(self, options):
    def RunRANDOMFORESTScikit(q):
      totalTimer = Timer()

      Log.Info("Loading dataset", self.verbose)
      trainData, labels = SplitTrainData(self.dataset)
      testData = LoadDataset(self.dataset[1])

      # Get all the parameters.
      e = re.search("-e (\d+)", options)
      c = re.search("-c (\s+)", options)
      d = re.search("-d (\s+)", options)
      s = re.search("-s (\d+)", options)
      mss = re.search("-mss (\d+)", options)
      msl = re.search("-msl (\d+)", options)
      nj = re.search("-nj (\d+)", options)

      self.n_estimators = 50 if not e else int(e.group(1))
      self.criterion = 'gini' if not c else str(c.group(1))
      self.max_depth = None if not d else int(d.group(1))
      self.seed = 0 if not s else int(s.group(1))
      self.min_samples_split = 2 if not mss else int(mss.group(1))
      self.min_samples_leaf = 1 if not msl else int(msl.group(1))
      self.n_jobs = 1 if not nj else int(nj.group(1))
      try:
        with totalTimer:
          self.model = self.BuildModel(trainData, labels)
          # Run Random Forest Classifier on the test dataset.
          self.model.predict(testData)
      except Exception as e:
        Log.Debug(str(e))
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)

      return time

    return timeout(RunRANDOMFORESTScikit, self.timeout)

  '''
  Perform the Random Forest Classifier. If the method has been
  successfully completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform Random Forest Classifier.", self.verbose)

    results = None
    if len(self.dataset) >= 2:
      results = self.RANDOMFORESTScikit(options)

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
