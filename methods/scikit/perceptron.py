'''
  @file perceptron.py
  @author Anand Soni

  Perceptron classification with scikit.
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
from sklearn.linear_model import Perceptron

'''
This class implements the Perceptron benchmark.
'''
class PERCEPTRON(object):

  ''' 
  Create the Perceptron benchmark instance.
  
  @param dataset - Input dataset to perform Perceptron classification on.
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
    p = Perceptron(n_iter=self.iterations)
    p.fit(data, responses)
    return p

  '''
  Use the scikit libary to implement Perceptron.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not 
  successful.
  '''
  def PerceptronScikit(self, options):
    def RunPerceptronScikit(q):
      totalTimer = Timer()

      # Load input dataset.
      # If the dataset contains two files then the second file is the test file.
      Log.Info("Loading dataset", self.verbose)
      if len(self.dataset) >= 2:
        testSet = LoadDataset(self.dataset[1])
      else:
        Log.Fatal("This method requires atleast two datasets.")

      # Gather all parameters.
      s = re.search('-i (\d+)', options)
      self.iterations = 1000 if not s else int(s.group(1))
      
      # Use the last row of the training set as the responses.  
      X, y = SplitTrainData(self.dataset)

      try:
        with totalTimer:
          # Perform perceptron classification.
          self.model = self.BuildModel(X, y)
          predictedlabels = self.model.predict(testSet)
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunPerceptronScikit, self.timeout)

  '''
  Perform Perceptron Classification. If the method has been successfully completed 
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not 
  successful.
  '''
  def RunTiming(self, options):
    Log.Info("Perform Perceptron Classification.", self.verbose)

    return self.PerceptronScikit(options)
  
  '''
  Run all the metrics for Perceptron classification.
  '''
  def RunMetrics(self, options):
    if len(self.dataset) >= 3:

      # Check if we need to create a model.
      if not self.model:
        trainData, labels = SplitTrainData(self.dataset)
        self.model = self.BuildModel(trainData, labels)

      testData = LoadDataset(self.dataset[1])
      truelabels = LoadDataset(self.dataset[2])

      #probabilities = self.model.predict_proba(testData)
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
      metrics_dict = {}
      metrics_dict['Avg Accuracy'] = AvgAcc
      metrics_dict['MultiClass Precision'] = AvgPrec
      metrics_dict['MultiClass Recall'] = AvgRec
      metrics_dict['MultiClass FMeasure'] = AvgF
      metrics_dict['MultiClass Lift'] = AvgLift
      metrics_dict['MultiClass MCC'] = AvgMCC
      metrics_dict['MultiClass Information'] = AvgInformation
      return metrics_dict

    else:
      Log.Fatal("This method requires three datasets.")
