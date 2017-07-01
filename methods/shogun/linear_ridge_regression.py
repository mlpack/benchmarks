'''
  @file linear_ridge_regression.py
  @author Ali Mohamed

  Linear Ridge Regression with shogun.
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
from modshogun import LinearRidgeRegression as LRR

'''
This class implements the Linear Ridge Regression benchmark.
'''
class LinearRidgeRegression(object):

  '''
  Create the Linear Ridge Regression benchmark instance.

  @param dataset - Input dataset to perform Linear Ridge Regression on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout

  '''
  Use the shogun libary to implement Linear Ridge Regression.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def LinearRidgeRegressionShogun(self, options):
    def RunLinearRidgeRegressionShogun(q):
      totalTimer = Timer()

      # Load input dataset.
      # If the dataset contains two files then the second file is the responses
      # file.
      Log.Info("Loading dataset", self.verbose)
      if len(self.dataset) >= 2:
        testSet = np.genfromtxt(self.dataset[1], delimiter=',')

      # Use the last row of the training set as the responses.
      X, y = SplitTrainData(self.dataset)
      if "alpha" in options:
        tau = float(options.pop("alpha"))
      else:
        Log.Fatal("Required parameter 'alpha' not specified!")
        raise Exception("missing parameter")

      if len(options) > 0:
        Log.Fatal("Unknown parameters: " + str(options))
        raise Exception("unknown parameters")

      try:
        with totalTimer:
          # Perform linear ridge regression.
          model = LRR(tau, RealFeatures(X.T), RegressionLabels(y))
          model.train()

          if len(self.dataset) >= 2:
            model.apply_regression(RealFeatures(testSet.T))

      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunLinearRidgeRegressionShogun, self.timeout)

  '''
  Perform Linear Ridge Regression. If the method has been successfully completed
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform Linear Ridge Regression.", self.verbose)

    results = self.LinearRidgeRegressionShogun(options)
    if results < 0:
      return results

    metrics = {'Runtime' : results}

    if len(self.dataset) >= 3:

      X, y = SplitTrainData(self.dataset)
      if "alpha" in options:
        tau = float(options.pop("alpha"))
      else:
        Log.Fatal("Required parameter 'alpha' not specified!")
        raise Exception("missing parameter")

      if len(options) > 0:
        Log.Fatal("Unknown parameters: " + str(options))
        raise Exception("unknown parameters")
      model = LRR(tau, RealFeatures(X.T), RegressionLabels(y))
      model.train()

      testData = LoadDataset(self.dataset[1])
      truelabels = LoadDataset(self.dataset[2])

      predictedlabels = model.apply_regression(RealFeatures(testData.T)).get_labels()

      SimpleMSE = Metrics.SimpleMeanSquaredError(truelabels, predictedlabels)
      metrics['Simple MSE'] = SimpleMSE
      return metrics

    else:
      Log.Fatal("This method requires three datasets!")
