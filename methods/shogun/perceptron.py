'''
  @file perceptron.py
  @author Anand Soni

  Perceptron Classification with shogun.
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
from modshogun import Perceptron
from modshogun import RealFeatures, MulticlassLabels

'''
This class implements the Perceptron benchmark.
'''
class PERCEPTRON(object):

  '''
  Create the Perceptron benchmark instance.

  @param dataset - Input dataset to perform Perceptron on.
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
  @param responses - The responses for the train set.
  @return The created model.
  '''
  def BuildModel(self, data, responses):
    # Create and train the classifier.
    model = AveragedPerceptron(RealFeatures(data.T), MulticlassLabels(responses))
    model.set_learn_rate(1.0)
    model.set_max_iter(self.iterations)
    model.train()
    return model

  '''
  Use the shogun libary to implement Perceptron.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def PerceptronShogun(self, options):
    def RunPerceptronShogun(q):
      totalTimer = Timer()
      # Load input dataset.
      # If the dataset contains two files then the second file is the test file.
      Log.Info("Loading dataset", self.verbose)
      try:
        if len(self.dataset) >= 2:
          testSet = LoadDataset(self.dataset[1])
        else:
          Log.Fatal("This method requires atleast two datasets.")

          # Use the last row of the training set as the responses.
          X, y = SplitTrainData(self.dataset)

          # Gather all parameters.
          s = re.search('-n (\d+)', options)
          self.iterations = 1000 if not s else int(s.group(1))

          with totalTimer:
            # Perform perceptron classification.
            self.model = BuildModel(X, y)
            self.model.set_features(RealFeatures(testSet.T))
            self.predictions = self.model.apply()
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunPerceptronShogun, self.timeout)

  '''
  Perform Perceptron classification. If the method has been successfully completed
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform Perceptron classification.", self.verbose)

    results = self.PerceptronShogun(options)
    if results < 0:
      return results

    metrics = {'Runtime' : results}

    if len(self.dataset) >= 3:

      # Check if we need to create a model.
      if not self.model:
        trainData, responses = SplitTrainData(self.dataset)
        self.model = self.BuildModel(trainData, responses)
        self.model.set_features(RealFeatures(testSet.T))
        self.predictions = self.model.apply()
      
      testData = LoadDataset(self.dataset[1])
      truelabels = LoadDataset(self.dataset[2])

      confusionMatrix = Metrics.ConfusionMatrix(truelabels, self.predictions)
      metrics['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metrics['LFT'] = Metrics.LiftMultiClass(confusionMatrix)
      metrics['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metrics['FMeasure'] = Metrics.AvgFMeasure(confusionMatrix)
      metrics['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metrics['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metrics['MSE'] = Metrics.SimpleMeanSquaredError(truelabels, predictedlabels)
      metrics['Information'] = Metrics.AvgMPIArray(confusionMatrix, truelabels, predictedlabels)

    return metrics
