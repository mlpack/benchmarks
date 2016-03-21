'''
  @file lasso.py
  @author Youssef Emad El-Din

  Lasso Regression with shogun.
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
from modshogun import RegressionLabels, RealFeatures
from modshogun import LeastAngleRegression

'''
This class implements the Lasso Regression benchmark.
'''
class LASSO(object):

  '''
  Create the Lasso Regression benchmark instance.

  @param dataset - Input dataset to perform Lasso Regression on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout

  '''
  Use the shogun libary to implement Linear Regression.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def LASSOShogun(self, options):
    def RunLASSOShogun(q):
      totalTimer = Timer()

      # Load input dataset.
      # If the dataset contains two files then the second file is the responses
      # file.
      try:
        Log.Info("Loading dataset", self.verbose)
        if len(self.dataset) == 2:
          testSet = np.genfromtxt(self.dataset[1], delimiter=',')

          # Get all the parameters.
          lambda1 = re.search("-l (\d+)", options)
          lambda1 = 0.0 if not lambda1 else int(lambda1.group(1))

        # Use the last row of the training set as the responses.
        X, y = SplitTrainData(self.dataset)

        with totalTimer:
          model = LeastAngleRegression(lasso=True)
          model.set_max_l1_norm(lambda1) 
          model.set_labels(RegressionLabels(y))
          model.train(RealFeatures(X.T))

      except Exception as e:
        print(e)
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunLASSOShogun, self.timeout)

  '''
  Perform Lasso Regression. If the method has been successfully completed
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunTiming(self, options):
    Log.Info("Perform Lasso Regression.", self.verbose)

    return self.LASSOShogun(options)

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
      AvgInformation = Metrics.AvgMPIArray(confusionMatrix, truelabels, self.predictions)
      SimpleMSE = Metrics.SimpleMeanSquaredError(truelabels, self.predictions)
      metric_results = (AvgAcc, AvgPrec, AvgRec, AvgF, AvgLift, AvgMCC, AvgInformation)
      metrics_dict = {}
      metrics_dict['Avg Accuracy'] = AvgAcc
      metrics_dict['MultiClass Precision'] = AvgPrec
      metrics_dict['MultiClass Recall'] = AvgRec
      metrics_dict['MultiClass FMeasure'] = AvgF
      metrics_dict['MultiClass Lift'] = AvgLift
      metrics_dict['MultiClass MCC'] = AvgMCC
      metrics_dict['MultiClass Information'] = AvgInformation
      metrics_dict['Simple MSE'] = SimpleMSE
      return metrics_dict
    else:
      Log.Fatal("This method requires three datasets!")

    # now the predictions are in self.predictions

