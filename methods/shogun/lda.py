'''
  @file lda.py
  @author Chirag Pabbaraju

  Linear Discriminant Analysis for Multiclass classification with shogun.
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

# Import the metrics definitions path.
metrics_folder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../metrics")))
if metrics_folder not in sys.path:
  sys.path.insert(0, metrics_folder)

from log import *
from timer import *
from definitions import *
from misc import *

from modshogun import MCLDA, RealFeatures, MulticlassLabels

'''
This class implements the Linear Discriminant Analysis benchmark.
'''
class LDA(object):
  
  '''
  Create the Linear Discriminant Analysis benchmark instance.

  @param dataset - Input dataset to perform Linear Discriminant Analysis on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.model = None
    self.predictions = None
    self.tolerance = 0.0001
    self.store = True

  '''
  Use the shogun library to implement Linear Discriminant Analysis.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not successful.
  '''
  def LDAShogun(self, options):
    @timeout_decorator.timeout(self.timeout)
    def RunLDAShogun():
      totalTimer = Timer()
      
      # Load input dataset.
      # If the dataset contains two files then the second file is the test file.
      try:
        if len(self.dataset) > 1:
          testSet = LoadDataset(self.dataset[1])

        # Use the last row of the training set as the responses.
        trainSet, trainLabels = SplitTrainData(self.dataset)
        # if the labels are not in {0,1,2,...,num_classes-1}, map them to this set and store the mapping
        # shogun's MCLDA class requires the labels to be in {0,1,2,...,num_classes-1}
        distinctLabels = list(set(trainLabels))
        mapping = {}
        reverseMapping = {}
        idx = 0
        for label in distinctLabels:
          mapping[label] = idx
          reverseMapping[idx] = label
          idx += 1
        for i in range(len(trainLabels)):
          trainLabels[i] = mapping[trainLabels[i]]

        trainFeat = RealFeatures(trainSet.T)
        trainLabels = MulticlassLabels(trainLabels)
        # Gather optional parameters.
        if "tolerance" in options:
          self.tolerance = float(options.pop("tolerance"))

        if "store" in options:
          self.store = bool(options.pop("store"))

        if (len(options) > 0):
          Log.Fatal("Unknown parameters: " + str(options))
          raise Exception("unknown parameters")

        with totalTimer:
          self.model = MCLDA(trainFeat, trainLabels, self.tolerance, self.store)
          self.model.train()

        if (len(self.dataset) > 0):
          self.predictions = self.model.apply_multiclass(RealFeatures(testSet.T))
          self.predictions = self.predictions.get_labels()
          # reverse map the predicted labels to actual labels
          for i in range(len(self.predictions)):
            self.predictions[i] = reverseMapping[self.predictions[i]]

      except Exception as e:
        Log.Info("Exception: " + str(e))
        return [-1]

      time = totalTimer.ElapsedTime()
      if (len(self.dataset) > 1):
        return [time, self.predictions]
      return [time]

    try:
      return RunLDAShogun()
    except timeout_decorator.TimeoutError:
      Log.Info("Timeout error")
      return [-1]

  '''
  Perform LDA. If the method has been successfully completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform LDA.", self.verbose)

    results = self.LDAShogun(options)
    if results[0] < 0:
      return {"Runtime" : -1}

    metrics = {"Runtime" : results}
    if len(self.dataset) >= 3:
      truelabels = LoadDataset(self.dataset[2])
      confusionMatrix = Metrics.ConfusionMatrix(truelabels, self.predictions)
      metrics['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metrics['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metrics['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metrics['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metrics['FMeasure'] = Metrics.AvgFMeasure(confusionMatrix)
      metrics['Lift'] = Metrics.LiftMultiClass(confusionMatrix)
      metrics['Information'] = Metrics.AvgMPIArray(confusionMatrix, truelabels, self.predictions)
      metrics['MSE'] = Metrics.SimpleMeanSquaredError(truelabels, self.predictions)

    return metrics
