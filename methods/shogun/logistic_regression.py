'''
  @file logistic_regression.py
  @author Marcus Edel

  Logistic Regression with shogun.
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

import numpy as np
from modshogun import MulticlassLogisticRegression
from modshogun import RealFeatures, MulticlassLabels

'''
This class implements the Logistic Regression benchmark.
'''
class LogisticRegression(object):

  ''' 
  Create the Logistic Regression benchmark instance.
  
  @param dataset - Input dataset to perform Logistic Regression on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.predictions = None

  '''
  Use the shogun libary to implement Logistic Regression.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not 
  successful.
  '''
  def LogisticRegressionShogun(self, options):
    def RunLogisticRegressionShogun(q):
      totalTimer = Timer()

      # Load input dataset.
      # If the dataset contains two files then the second file is the test
      # file.
      try:
        Log.Info("Loading dataset", self.verbose)
        if len(self.dataset) >= 2:
          testSet = np.genfromtxt(self.dataset[1], delimiter=',')
          trainFile = self.dataset[0]
        else:
          trainFile = self.dataset
          
        X = np.genfromtxt(trainFile, delimiter=',')
        y = X[:, (X.shape[1] - 1)]
        X = X[:,:-1]

        # Get the regularization value.
        z = re.search("-l (\d+)", options)
        z = 0 if not z else int(z.group(1))

        with totalTimer:
          # Perform logistic regression.
          model = MulticlassLogisticRegression(z, RealFeatures(X.T), MulticlassLabels((y))
          model.train()
          
          if len(self.dataset) == 2:
            pred = classifier.apply(RealFeatures(testSet.T))
            self.predictions = pred.get_labels()

      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunLogisticRegressionShogun, self.timeout)

  '''
  Perform Logistic Regression. If the method has been successfully completed 
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not 
  successful.
  '''
  def RunTiming(self, options):
    Log.Info("Perform Logistic Regression.", self.verbose)

    return self.LogisticRegressionShogun(options)

  def RunMetrics(self, options):
    if not self.predictions:
      self.RunTiming(options)

      testData = LoadDataset(self.dataset[1])
      truelabels = LoadDataset(self.dataset[2])

      confusionMatrix = Metrics.ConfusionMatrix(truelabels, self.predictions)
      AvgAcc = Metrics.AverageAccuracy(confusionMatrix)
      AvgPrec = Metrics.AvgPrecision(confusionMatrix)
      AvgRec = Metrics.AvgRecall(confusionMatrix)
      AvgF = Metrics.AvgFMeasure(confusionMatrix)
      AvgLift = Metrics.LiftMultiClass(confusionMatrix)
      AvgMCC = Metrics.MCCMultiClass(confusionMatrix)
      #MeanSquaredError = Metrics.MeanSquaredError(labels, probabilities, confusionMatrix)
      AvgInformation = Metrics.AvgMPIArray(confusionMatrix, truelabels, predictedlabels)
      metric_results = (AvgAcc, AvgPrec, AvgRec, AvgF, AvgLift, AvgMCC, AvgInformation)
      Log.Debug(str(metric_results))
    else:
      Log.Fatal("This method requires three datasets!")
  
    # now the predictions are in self.predictions

