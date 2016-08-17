'''
  @file knc.py
  @author Marcus Edel

  Classifier implementing the k-nearest neighbors vote with shogun.
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
from modshogun import RealFeatures, MulticlassLabels, KNN, EuclideanDistance

'''
This class implements the Support vector machines benchmark.
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

  '''
  Build the model for the k-nearest neighbors Classifier.

  @param data - The train data.
  @param labels - The labels for the train set.
  @return The created model.
  '''
  def BuildModel(self, data, labels, options):
    # Get all the parameters.
    n = re.search("-n (\d+)", options)

    self.n_neighbors = 5 if not n else int(n.group(1))

    distance = EuclideanDistance(data, data)
    from modshogun import KNN_KDTREE
    knc = KNN(self.n_neighbors, distance, labels, KNN_KDTREE)
    knc.set_leaf_size(30)
    knc.train()

    return knc

  '''
  Use the shogun libary to implement the k-nearest neighbors Classifier.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def KNCShogun(self, options):
    def RunKNCShogun(q):
      totalTimer = Timer()

      Log.Info("Loading dataset", self.verbose)
      trainData, labels = SplitTrainData(self.dataset)
      trainData = RealFeatures(trainData.T)
      labels = MulticlassLabels(labels)
      testData = RealFeatures(LoadDataset(self.dataset[1]).T)

      try:
        with totalTimer:
          self.model = self.BuildModel(trainData, labels, options)
          # Run the k-nearest neighbors Classifier on the test dataset.
          self.model.apply(testData).get_labels()
      except Exception as e:
        Log.Debug(str(e))
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)

      return time

    return timeout(RunKNCShogun, self.timeout)

  '''
  Perform the k-nearest neighbors Classifier. If the method has been
  successfully completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform KNC.", self.verbose)

    results = None
    if len(self.dataset) >= 2:
      results = self.KNCShogun(options)

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
        self.model = self.BuildModel(trainData, labels, options)

      testData = LoadDataset(self.dataset[1])
      truelabels = LoadDataset(self.dataset[2])
      predictedlabels = self.model.apply(RealFeatures(testData.T)).get_labels()

      confusionMatrix = Metrics.ConfusionMatrix(truelabels, predictedlabels)
      metrics['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metrics['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metrics['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metrics['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metrics['MSE'] = Metrics.SimpleMeanSquaredError(truelabels, predictedlabels)

    return metrics
