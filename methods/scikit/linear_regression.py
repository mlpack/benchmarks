'''
  @file linear_regression.py
  @author Marcus Edel, Anand Soni

  Linear Regression with scikit.
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
from sklearn.linear_model import LinearRegression as SLinearRegression

'''
This class implements the Linear Regression benchmark.
'''
class LinearRegression(object):

  '''
  Create the Linear Regression benchmark instance.

  @param dataset - Input dataset to perform Linear Regression on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.model = None

  '''
  Build the model for the Linear Regression.

  @param data - The train data.
  @param responses - The responses for the training set.
  @return The created model.
  '''
  def BuildModel(self, data, responses):
    # Create and train the classifier.
    lr = SLinearRegression()
    lr.fit(data, responses)
    return lr

  '''
  Use the scikit libary to implement Linear Regression.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def LinearRegressionScikit(self, options):
    def RunLinearRegressionScikit(q):
      totalTimer = Timer()

      if len(options) > 0:
        Log.Fatal("Unknown parameters: " + str(options))
        raise Exception("unknown parameters")

      # Load input dataset.
      # If the dataset contains two files then the second file is the test file.
      Log.Info("Loading dataset", self.verbose)
      if len(self.dataset) >= 2:
        testSet = LoadDataset(self.dataset[1])

      # Use the last row of the training set as the responses.
      X, y = SplitTrainData(self.dataset)

      try:
        with totalTimer:
          # Perform linear regression.
          self.model = self.BuildModel(X,y)
          b = self.model.coef_

          if len(self.dataset) >= 2:
            self.model.predict(testSet)
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunLinearRegressionScikit, self.timeout)

  '''
  Perform Linear Regression. If the method has been successfully completed
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform Linear Regression.", self.verbose)
    results = self.LinearRegressionScikit(options)

    if results < 0:
      return results

    # Datastructure to store the results.
    metrics = {'Runtime' : results}

    if len(self.dataset) >= 3:

      # Check if we need to create a model.
      if not self.model:
        trainData, labels = SplitTrainData(self.dataset)
        self.model = self.BuildModel(trainData, labels)

      testData = LoadDataset(self.dataset[1])
      truelabels = LoadDataset(self.dataset[2])

      predictedlabels = np.rint(self.model.predict(testData))

      confusionMatrix = Metrics.ConfusionMatrix(truelabels, predictedlabels)
      AvgAcc = Metrics.AverageAccuracy(confusionMatrix)
      AvgPrec = Metrics.AvgPrecision(confusionMatrix)
      AvgRec = Metrics.AvgRecall(confusionMatrix)
      AvgF = Metrics.AvgFMeasure(confusionMatrix)
      AvgLift = Metrics.LiftMultiClass(confusionMatrix)
      AvgMCC = Metrics.MCCMultiClass(confusionMatrix)
      AvgInformation = Metrics.AvgMPIArray(confusionMatrix, truelabels, predictedlabels)
      SimpleMSE = Metrics.SimpleMeanSquaredError(truelabels, predictedlabels)
      metric_results = (AvgAcc, AvgPrec, AvgRec, AvgF, AvgLift, AvgMCC, AvgInformation)

      metrics['Avg Accuracy'] = AvgAcc
      metrics['MultiClass Precision'] = AvgPrec
      metrics['MultiClass Recall'] = AvgRec
      metrics['MultiClass FMeasure'] = AvgF
      metrics['MultiClass Lift'] = AvgLift
      metrics['MultiClass MCC'] = AvgMCC
      metrics['MultiClass Information'] = AvgInformation
      metrics['Simple MSE'] = SimpleMSE

    return metrics
