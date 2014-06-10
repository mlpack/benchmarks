'''
  @file nbc.py
  @author Marcus Edel

  Naive Bayes Classifier with scikit.
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
from sklearn.naive_bayes import MultinomialNB

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
  Use the scikit libary to implement Naive Bayes Classifier.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not 
  successful.
  '''
  def NBCScikit(self, options):
    def RunNBCScikit(q):
      totalTimer = Timer()
      
      Log.Info("Loading dataset", self.verbose)
      # Load train and test dataset.
      trainData = np.genfromtxt(self.dataset[0], delimiter=',')
      testData = np.genfromtxt(self.dataset[1], delimiter=',')

      # Labels are the last row of the training set.
      labels = trainData[:, (trainData.shape[1] - 1)]
      trainData = trainData[:,:-1]

      try:
        with totalTimer:      
          # Create and train the classifier.
          nbc = MultinomialNB()
          nbc.fit(trainData, labels)
          # Run Naive Bayes Classifier on the test dataset.
          predictedlabels = nbc.predict(testData)
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)

      # Okay we have to check if we have enough datasets in the dataset list to 
      # perform the additional evaluations.
      if len(self.dataset) == 3:
        # We need the propabilities, but instead of generating a new model we 
        # resuse the model. So the only thing we need to do is to calculate the
        # propabilities and run the metrics.
        probabilities = nbc.predict_proba(testData)
        truelabels = np.genfromtxt(self.dataset[2], delimiter=',')
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


      return time

    return timeout(RunNBCScikit, self.timeout)
  
  '''
  Get probabilities for all instances. This method returns a matrix
  containing the probabilities of each test instance of falling in 
  a particular class.
  '''
  def GetAllProbabilities(self):
    testData = np.genfromtxt(self.dataset[1], delimiter=',')
    nbc = MultinomialNB()
    probabilities = nbc.predict_proba(testData)
    probabilities = np.array(probabilities)
    return probabilities

  '''
  Get predicted labels for all test instances. This method returns the
  predicted labels for all instances of the test data.
  '''
  def GetPredictedClasses(self):
    testData = np.genfromtxt(self.dataset[1], delimiter=',')
    nbc = MultinomialNB()
    predicted = nbc.predict(testData)
    predicted = np.array(predicted)
    return predicted

  '''
  @param labels : the file containing true labels for the test data
  Perform all metrics from the benchmarking system on this method.
  '''
  def RunMetrics(self, labels):
    truelabels = np.genfromtxt(labels, delimiter=',')
    predictedlabels = GetPredictedClasses()
    probabilities = GetAllProbabilities()
    confusionMatrix = Metrics.ConfusionMatrix(truelabels, predictedlabels)
    #self.VisualizeConfusionMatrix(confusionMatrix)
    AvgAcc = Metrics.AverageAccuracy(confusionMatrix)
    AvgPrec = Metrics.AvgPrecision(confusionMatrix)
    AvgRec = Metrics.AvgRecall(confusionMatrix)
    AvgF = Metrics.AvgFMeasure(confusionMatrix)
    AvgLift = Metrics.LiftMultiClass(confusionMatrix)
    AvgMCC = Metrics.MCCMultiClass(confusionMatrix)
    #MeanSquaredError = Metrics.MeanSquaredError(labels, probabilities, confusionMatrix)
    AvgInformation = Metrics.AvgMPIArray(confusionMatrix, truelabels, predictedlabels)

  '''
  Perform Naive Bayes Classifier. If the method has been successfully 
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not 
  successful.
  '''
  def RunMethod(self, options):
    Log.Info("Perform NBC.", self.verbose)

    if (len(self.dataset) != 2) and (len(self.dataset) != 3):
      Log.Fatal("This method requires two or three datasets.")
      return -1

    if len(self.dataset) == 2 or len(self.dataset) == 3:
      return self.NBCScikit(options)

