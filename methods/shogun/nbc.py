'''
  @file nbc.py
  @author Marcus Edel

  Naive Bayes Classifier with shogun.
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
from modshogun import RealFeatures, MulticlassLabels, GaussianNaiveBayes

'''
This class implements the Naive Bayes Classifier benchmark.
'''
class NBC(object):

  '''
  Create the Naive Bayes Classifier benchmark instance.

  @param dataset - Input dataset to perform NBC on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout

  '''
  Use the shogun libary to implement Naive Bayes Classifier.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def NBCShogun(self, options):
    def RunNBCShogun(q):
      totalTimer = Timer()

      Log.Info("Loading dataset", self.verbose)
      try:
        # Load train and test dataset.
        trainData = np.genfromtxt(self.dataset[0], delimiter=',')
        testData = np.genfromtxt(self.dataset[1], delimiter=',')

        if len(options) > 0:
          Log.Fatal("Unknown parameters: " + str(options))
          raise Exception("unknown parameters")

        # Labels are the last row of the training set.
        labels = MulticlassLabels(trainData[:, (trainData.shape[1] - 1)])

        with totalTimer:
          # Transform into features.
          trainFeat = RealFeatures(trainData[:,:-1].T)
          testFeat = RealFeatures(testData.T)

          # Create and train the classifier.
          nbc = GaussianNaiveBayes(trainFeat, labels)
          nbc.train()

          # Run Naive Bayes Classifier on the test dataset.
          nbc.apply(testFeat).get_labels()
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunNBCShogun, self.timeout)

  '''
  Perform Naive Bayes Classifier. If the method has been successfully completed
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform NBC.", self.verbose)

    if len(self.dataset) != 2:
      Log.Fatal("This method requires two datasets.")
      return -1

    results = self.NBCShogun(options)
    if results < 0:
      return results

    metrics = {'Runtime' : results}

    if len(self.dataset) == 3:
    # Check if the files to calculate the different metric are available.
      cmd = shlex.split("methods/shogun/nbc " + self.dataset[0]
           + " " + self.dataset[1])
      if not CheckFileAvailable("shogun_labels.csv") or not CheckFileAvailable("shogun_probs.csv"):
        try:
          s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False,
              timeout=self.timeout)
        except subprocess.TimeoutExpired as e:
          Log.Warn(str(e))
          return -2
        except Exception as e:
          Log.Fatal("Could not execute command: " + str(cmd))
          return -1

      testData = LoadDataset(self.dataset[1])
      truelabels = LoadDataset(self.dataset[2])
      probabilities = LoadDataset("shogun_probs.csv")
      predictedlabels = LoadDataset("shogun_labels.csv")

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
