'''
  @file qda.py
  @author Marcus Edel

  Quadratic Discriminant Analysis with scikit.
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
from sklearn.qda import QDA as SQDA

'''
This class implements the Quadratic Discriminant Analysis benchmark.
'''
class QDA(object):

  '''
  Create the Quadratic Discriminant Analysis benchmark instance.

  @param dataset - Input dataset to perform QDA on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.predictions = None
    self.model = None

  '''
  Build the model for the Quadratic Discriminant Analysis.

  @param data - The train data.
  @param labels - The labels for the train set.
  @return The created model.
  '''
  def BuildModel(self, data, labels):
    # Create and train the classifier.
    qda = SQDA()
    qda.fit(data, labels)
    return qda

  '''
  Use the scikit libary to implement the Quadratic Discriminant Analysis.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def QDAScikit(self, options):
    def RunQDAScikit(q):
      totalTimer = Timer()

      Log.Info("Loading dataset", self.verbose)
      trainData, labels = SplitTrainData(self.dataset)
      testData = LoadDataset(self.dataset[1])

      if len(options) > 0:
        Log.Fatal("Unknown parameters: " + str(options))
        raise Exception("unknown parameters")

      try:
        with totalTimer:
          self.model = self.BuildModel(trainData, labels)
          # Run Quadratic Discriminant Analysis on the test dataset.
          self.predictions = self.model.predict(testData)
      except Exception as e:
        Log.Debug(str(e))
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put((time, self.predictions))

      return time

    result = timeout(RunQDAScikit, self.timeout)
    if len(result) > 1:
      self.predictions = result[1]
      
    return result[0]

  '''
  Perform the Quadratic Discriminant Analysis. If the method has been
  successfully completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform QDA.", self.verbose)
    results = None

    if len(self.dataset) >= 2:
      results = self.QDAScikit(options)
      if results < 0:
        return results
    else:
      Log.Fatal("This method requires two datasets.")

    # Datastructure to store the results.
    metrics = {'Runtime' : results}

    if len(self.dataset) >= 3:

      # Check if we need to create a model.
      truelabels = LoadDataset(self.dataset[2])

      confusionMatrix = Metrics.ConfusionMatrix(truelabels, self.predictions)
      
      metrics['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metrics['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metrics['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metrics['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metrics['MSE'] = Metrics.SimpleMeanSquaredError(truelabels, self.predictions)

    return metrics
