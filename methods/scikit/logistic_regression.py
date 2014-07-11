'''
  @file logistic_regression.py
  @author Anand Soni

  Logistic Regression with scikit.
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

  '''
  Build the model for the Logistic Regression.

  @param data - The train data.
  @param labels - The labels for the train set.
  @return The created model.
  '''
  def BuildModel(self, data, labels):
    # Create and train the classifier.
    lr = SLogisticRegression()
    lr.fit(data, labels)
    return lr

  '''
  Use the scikit libary to implement Logistic Regression.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not 
  successful.
  '''
  def LogisticRegressionScikit(self, options):
    def RunLogisticRegressionScikit(q):
      totalTimer = Timer()

      # Load input dataset.
      # If the dataset contains two files then the second file is the responses 
      # file.
      Log.Info("Loading dataset", self.verbose)
      if len(self.dataset) == 2:
        X = np.genfromtxt(self.dataset[0], delimiter=',')
        y = np.genfromtxt(self.dataset[1], delimiter=',')
      else:
        X = np.genfromtxt(self.dataset, delimiter=',')
        y = X[:, (X.shape[1] - 1)]
        X = X[:,:-1]

      try:
        with totalTimer:
          # Perform logistic regression.
          self.model = self.BuildModel(X,y)
          #model = SLogisticRegression()
          #model.fit(X, y, n_jobs=-1)
          b = self.model.coef_
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunLogisticRegressionScikit, self.timeout)

  '''
  Perform Logistic Regression. If the method has been successfully completed 
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not 
  successful.
  '''
  def RunTiming(self, options):
    Log.Info("Perform Logistic Regression.", self.verbose)

    return self.LogisticRegressionScikit(options)
  
  '''
  Run all the metrics for Logistic Regression.
  '''
  def RunMetrics(self, options):
    if len(self.dataset) >= 3:

      # Check if we need to create a model.
      if not self.model:
        trainData, labels = SplitTrainData(self.dataset)
        self.model = self.BuildModel(trainData, labels)

      testData = LoadDataset(self.dataset[1])
      truelabels = LoadDataset(self.dataset[2])

      probabilities = self.model.predict_proba(testData)
      predictedlabels = self.model.predict(testData)

      confusionMatrix = Metrics.ConfusionMatrix(truelabels, predictedlabels)
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
      Log.Fatal("This method requires three datasets.")
