'''
  @file qda.py
  @author Youssef Emad El-Din

  QDA Classifier with shogun.
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
import modshogun

'''
This class implements the QDA Classifier benchmark.
'''
class QDA(object):

  '''
  Create the QDA Classifier benchmark instance.

  @param dataset - Input dataset to perform QDA on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout

  '''
  Use the shogun libary to implement QDA Classifier.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def QDAShogun(self, options):
    def RunQDAShogun(q):
      totalTimer = Timer()

      Log.Info("Loading dataset", self.verbose)
      try:
        # Load train and test dataset.
        trainData = np.genfromtxt(self.dataset[0], delimiter=',')
        trainFeat = modshogun.RealFeatures(trainData[:,:-1].T)

        if len(self.dataset) == 2:
          testSet = np.genfromtxt(self.dataset[1], delimiter=',')
          testFeat = modshogun.RealFeatures(testData.T)

        if len(options) > 0:
          Log.Fatal("Unknown parameters: " + str(options))
          raise Exception("unknown parameters")

        # Labels are the last row of the training set.
        labels = modshogun.MulticlassLabels(trainData[:, (trainData.shape[1] - 1)])

        with totalTimer:

          model = modshogun.QDA(trainFeat, labels)
          model.train()
          if len(self.dataset) == 2:
            model.apply(testFeat).get_labels()
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunQDAShogun, self.timeout)

  '''
  Perform QDA Classifier. If the method has been successfully completed
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform QDA.", self.verbose)

    results = self.QDAShogun(options)
    if results < 0:
      return results

    metrics = {'Runtime' : results}

    if len(self.dataset) >= 3:
      trainData, labels = SplitTrainData(self.dataset)
      testData = LoadDataset(self.dataset[1])
      truelabels = LoadDataset(self.dataset[2])

      model = modshogun.QDA(modshogun.RealFeatures(trainData.T),modshogun.MulticlassLabels(labels))
      model.train()
      predictions = model.apply(modshogun.RealFeatures(testData.T)).get_labels()

      confusionMatrix = Metrics.ConfusionMatrix(truelabels, predictions)
      metrics['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metrics['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metrics['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metrics['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metrics['MSE'] = Metrics.SimpleMeanSquaredError(truelabels, predictions)

    return metrics
