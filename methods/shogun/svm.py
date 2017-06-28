'''
  @file svm.py
  @author Marcus Edel

  Support vector machines with shogun.
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
from modshogun import RealFeatures, MulticlassLabels, LibSVM
from modshogun import GaussianKernel, PolyKernel, LinearKernel, SigmoidKernel

'''
This class implements the Support vector machines benchmark.
'''
class SVM(object):

  '''
  Create the Support vector machines benchmark instance.

  @param dataset - Input dataset to perform SVM on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.model = None
    self.kernel = None
    self.C = 1.0
    self.gamma = 0.0

  '''
  Build the model for the Support vector machines.

  @param data - The train data.
  @param labels - The labels for the train set.
  @return The created model.
  '''
  def BuildModel(self, data, labels, options):
    if "kernel" in options:
      k = str(options.pop("kernel"))
    else:
      Log.Fatal("Required parameter 'kernel' not specified!")
      raise Exception("missing parameter")

    if "c" in options:
      self.C = float(options.pop("c"))
    if "gamma" in options:
      self.gamma = float(options.pop("gamma"))


    if k == "gaussian":
      self.kernel = GaussianKernel(data, data, 1)
    elif k == "polynomial":
      if "degree" in options:
        d = int(options.pop("degree"))
      else:
        d = 1

      self.kernel = PolyKernel(data, data, d, True)
    elif k == "linear":
      self.kernel = LinearKernel(data, data)
    elif k == "hyptan":
      self.kernel = SigmoidKernel(data, data, 2, 1.0, 1.0)
    else:
      self.kernel = GaussianKernel(data, data, 1)

    if len(options) > 0:
      Log.Fatal("Unknown parameters: " + str(options))
      raise Exception("unknown parameters")

    # Create and train the classifier.
    svm = LibSvm(self.C, self.kernel, labels)
    svm.train()
    return svm

  '''
  Use the shogun libary to implement the Support vector machines.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def SVMShogun(self, options):
    def RunSVMShogun(q):
      totalTimer = Timer()

      Log.Info("Loading dataset", self.verbose)
      trainData, labels = SplitTrainData(self.dataset)
      trainData = RealFeatures(trainData.T)
      labels = MulticlassLabels(labels)
      testData = RealFeatures(LoadDataset(self.dataset[1]).T)

      try:
        with totalTimer:
          self.model = self.BuildModel(trainData, labels, options)
          # Run Support vector machines on the test dataset.
          self.model.apply(testData).get_labels()
      except Exception as e:
        Log.Debug(str(e))
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)

      return time

    return timeout(RunSVMShogun, self.timeout)

  '''
  Perform the Support vector machines. If the method has been
  successfully completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform SVM.", self.verbose)

    results = None
    if len(self.dataset) >= 2:
      results = self.SVMShogun(options)

      if results < 0:
        return results
    else:
      Log.Fatal("This method requires two datasets.")

    # Datastructure to store the results.
    metrics = {'Runtime' : results}

    if len(self.dataset) >= 3:

      # Check if we need to create a model.
      if not self.model:
        trainData, labels = SplitTrainData(self.dataset)
        self.model = self.BuildModel(trainData, labels, options)

      testData = LoadDataset(self.dataset[1])
      truelabels = LoadDataset(self.dataset[2])
      predictedlabels = self.model.apply(RealFeatures(testData.T)).get_labels()

      confusionMatrix = Metrics.ConfusionMatrix(truelabels, predictedlabels)
      metrics['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metrics['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metrics['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metrics['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metrics['MSE'] = Metrics.SimpleMeanSquaredError(truelabels, predictedlabels)

    return metrics
