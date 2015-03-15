'''
  @file knc.py
  @author Marcus Edel

  Classifier implementing the k-nearest neighbors vote with scikit.
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
from sklearn.neighbors import KNeighborsClassifier

'''
This class implements the k-nearest neighbors Classifier benchmark.
'''
class KNC(object):

  '''
  Create the k-nearest neighbors Classifier benchmark instance.

  @param dataset - Input dataset to perform KNC on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.model = None
    self.n_neighbors = 5
    self.algorithm = 'kd_tree'
    self.leaf_size = 30
    self.metric = 'minkowski'

  '''
  Build the model for the k-nearest neighbors Classifier.

  @param data - The train data.
  @param labels - The labels for the train set.
  @return The created model.
  '''
  def BuildModel(self, data, labels):
    # Create and train the classifier.
    knc = KNeighborsClassifier(n_neighbors=self.n_neighbors,
                               algorithm=self.algorithm,
                               leaf_size=self.leaf_size,
                               metric=self.metric)
    knc.fit(data, labels)
    return knc

  '''
  Use the scikit libary to implement the k-nearest neighbors Classifier.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def KNCScikit(self, options):
    def RunKNCScikit(q):
      totalTimer = Timer()

      Log.Info("Loading dataset", self.verbose)
      trainData, labels = SplitTrainData(self.dataset)
      testData = LoadDataset(self.dataset[1])

      # Get all the parameters.
      n = re.search("-n (\d+)", options)
      a = re.search("-a (\s+)", options)
      l = re.search("-l (\d+)", options)
      m = re.search("-m (\s+)", options)

      self.n_neighbors = 5 if not n else int(n.group(1))
      self.algorithm = 'kd_tree' if not a else str(a.group(1))
      self.leaf_size = 30 if not l else int(l.group(1))
      self.metric = 'minkowski' if not m else str(m.group(1))

      try:
        with totalTimer:
          self.model = self.BuildModel(trainData, labels)
          # Run k-nearest neighbors Classifier on the test dataset.
          self.model.predict(testData)
      except Exception as e:
        Log.Debug(str(e))
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)

      return time

    return timeout(RunKNCScikit, self.timeout)

  '''
  Perform the k-nearest neighbors Classifier. If the method has been
  successfully completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunTiming(self, options):
    Log.Info("Perform KNC.", self.verbose)

    if len(self.dataset) >= 2:
      return self.KNCScikit(options)
    else:
      Log.Fatal("This method requires two datasets.")

  def RunMetrics(self, options):
    if len(self.dataset) >= 3:

      # Check if we need to create a model.
      if not self.model:
        trainData, labels = SplitTrainData(self.dataset)
        self.model = self.BuildModel(trainData, labels)

      testData = LoadDataset(self.dataset[1])
      truelabels = LoadDataset(self.dataset[2])

      predictedlabels = self.model.predict(testData)

      # Datastructure to store the results.
      metrics = {}

      confusionMatrix = Metrics.ConfusionMatrix(truelabels, predictedlabels)
      metrics['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metrics['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metrics['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metrics['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metrics['MSE'] = Metrics.SimpleMeanSquaredError(truelabels, predictedlabels)
      return metrics

    else:
      Log.Fatal("This method requires three datasets.")
