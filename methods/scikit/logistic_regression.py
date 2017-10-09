'''
  @file logistic_regression.py
  @author Anand Soni

  Logistic Regression with scikit.
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
from sklearn.linear_model import LogisticRegression as SLogisticRegression

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
    self.model = None
    self.predictions = None
    self.opts = {}

  '''
  Build the model for the Logistic Regression.

  @param data - The train data.
  @param responses - The responses for the train set.
  @return The created model.
  '''
  def BuildModel(self, data, responses):
    # Create and train the classifier.
    lr = SLogisticRegression(**self.opts)
    lr.fit(data, responses)
    return lr

  '''
  Use the scikit libary to implement Logistic Regression.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def LogisticRegressionScikit(self, options):
    @timeout_decorator.timeout(self.timeout)
    def RunLogisticRegressionScikit():
      totalTimer = Timer()

      # Load input dataset.
      # If the dataset contains two files then the second file is the test file.
      Log.Info("Loading dataset", self.verbose)
      if len(self.dataset) > 1:
        testSet = LoadDataset(self.dataset[1])

      # Use the last row of the training set as the responses.
      X, y = SplitTrainData(self.dataset)
      if "algorithm" in options:
        self.opts["solver"] = str(options.pop("algorithm"))
      if "epsilon" in options:
        self.opts["epsilon"] = float(options.pop("epsilon"))
      if "max_iterations" in options:
        self.opts["max_iter"] = int(options.pop("max_iter"))

      if len(options) > 0:
        Log.Fatal("Unknown parameters: " + str(options))
        raise Exception("unknown parameters")

      try:
        with totalTimer:
          # Perform logistic regression.
          self.model = self.BuildModel(X,y)
          b = self.model.coef_
          if len(self.dataset) > 1:
            self.predictions = self.model.predict(testSet)
      except Exception as e:
        return [-1]

      time = totalTimer.ElapsedTime()
      if len(self.dataset) > 1:
        return [time, self.predictions]

      return [time]

    try:
      result = RunLogisticRegressionScikit()
    except timeout_decorator.TimeoutError:
      return -1

    # Check for error, in this case the list doesn't contain extra information.
    if len(result) > 1:
       self.predictions = result[1]

    return result[0]

  '''
  Perform Logistic Regression. If the method has been successfully completed
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform Logistic Regression.", self.verbose)

    results = self.LogisticRegressionScikit(options)
    if results < 0:
      return results

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
