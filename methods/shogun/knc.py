'''
  @file knc.py
  @author Marcus Edel

  Classifier implementing the k-nearest neighbors vote with shogun.
'''

import os
import sys
import inspect
import timeout_decorator

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
from modshogun import RealFeatures, MulticlassLabels, KNN, EuclideanDistance, KNN_KDTREE

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
    self.predictions = None
    self.n_neighbors = 5

  '''
  Build the model for the k-nearest neighbors Classifier.

  @param data - The train data.
  @param labels - The labels for the train set.
  @return The created model.
  '''
  def BuildModel(self, data, labels, options):
    # Get all the parameters.
    if "k" in options:
      n_neighbors = int(options.pop("k"))
    else:
      Log.Fatal("Required parameter 'k' not specified!")
      raise Exception("missing parameter")

    if len(options) > 0:
      Log.Fatal("Unknown parameters: " + str(options))
      raise Exception("unknown parameters")

    distance = EuclideanDistance(data, data)
    knc = KNN(self.n_neighbors, distance, labels, KNN_KDTREE)
    knc.train()

    return knc

  '''
  Use the shogun libary to implement the k-nearest neighbors Classifier.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def KNCShogun(self, options):
    @timeout_decorator.timeout(self.timeout)
    def RunKNCShogun():
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
          self.predictions = self.model.apply_multiclass(testData).get_labels()
      except Exception as e:
        return [-1]

      time = totalTimer.ElapsedTime()
      if len(self.dataset) > 1:
        return [time, self.predictions]

      return [time]

    try:
      result = RunKNCShogun()
    except timeout_decorator.TimeoutError:
      return -1

    # Check for error, in this case the tuple doesn't contain extra information.
    if len(result) > 1:
      self.predictions = result[1]
      return result[0]

    return result[0]

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

      truelabels = LoadDataset(self.dataset[2])
      
      confusionMatrix = Metrics.ConfusionMatrix(truelabels, self.predictions)

      metrics['Avg Accuracy'] = Metrics.AverageAccuracy(confusionMatrix)
      metrics['MultiClass Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metrics['MultiClass Recall'] = Metrics.AvgRecall(confusionMatrix)
      metrics['MultiClass FMeasure'] = Metrics.AvgFMeasure(confusionMatrix)
      metrics['MultiClass Lift'] = Metrics.LiftMultiClass(confusionMatrix)
      metrics['MultiClass MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metrics['MultiClass Information'] = Metrics.AvgMPIArray(confusionMatrix, truelabels, self.predictions)
      metrics['Simple MSE'] = Metrics.SimpleMeanSquaredError(truelabels, self.predictions)

    return metrics
