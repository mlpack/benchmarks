'''
  @file perceptron.py
  @author Marcus Edel

  Perceptron Classifier with mlpy.
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
import mlpy

'''
This class implements the Perceptron benchmark.
'''
class PERCEPTRON(object):

  '''
  Create the Perceptron benchmark instance.

  @param dataset - Input dataset to perform the Perceptron Classifier on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.model = None
    self.iterations = 1000

  '''
  Build the model for the Perceptron.

  @param data - The train data.
  @param responses - The responses for the training set.
  @return The created model.
  '''
  def BuildModel(self, data, responses):
    # Create and train the classifier.
    model = mlpy.Perceptron(**self.opts)
    model.learn(data, responses)
    return model

  '''
  Use the mlpy libary to implement the Perceptron.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def PerceptronMlpy(self, options):
    def RunPerceptronMlpy(q):
      totalTimer = Timer()

      # Load input dataset.
      # If the dataset contains two files then the second file is the test file.
      Log.Info("Loading dataset", self.verbose)
      if len(self.dataset) >= 2:
        testSet = LoadDataset(self.dataset[1])
      else:
        Log.Fatal("This method requires atleast two datasets.")

      # Use the last row of the training set as the responses.
      X, y = SplitTrainData(self.dataset)

      self.opts = {}
      self.opts["alpha"] = 0.1
      self.opts["thr"] = 0.05
      if "max_iterations" in options:
        self.opts["maxiters"] = int(options.pop("max_iterations"))

      if len(options) > 0:
        Log.Fatal("Unknown parameters: " + str(options))
        raise Exception("unknown parameters")

      try:
        with totalTimer:
          # # Perform perceptron classification.
          self.model = self.BuildModel(X, y)

          if len(self.dataset) >= 2:
            #prediction on the test data.
            pred = model.pred(testSet)
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)

      return time

    return timeout(RunPerceptronMlpy, self.timeout)

  '''
  Perform the Perceptron Classifier. If the method has been successfully
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform Perceptron.", self.verbose)

    results = self.PerceptronMlpy(options)
    if results < 0:
      return results

    metrics = {'Runtime' : results}

    if len(self.dataset) >= 2:

      # Check if we need to create a model.
      if not self.model:
        trainData, labels = SplitTrainData(self.dataset)
        self.model = self.BuildModel(trainData, labels)

      testData = LoadDataset(self.dataset[1])
      truelabels = LoadDataset(self.dataset[2])
      predictedlabels = self.model.pred(testData)

      confusionMatrix = Metrics.ConfusionMatrix(truelabels, predictedlabels)
      metrics['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metrics['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metrics['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metrics['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metrics['MSE'] = Metrics.SimpleMeanSquaredError(truelabels, predictedlabels)

    return metrics
