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

from log import *
from timer import *

import numpy as np
from shogun.Features import RealFeatures, MulticlassLabels
from shogun.Classifier import GaussianNaiveBayes

'''
This class implements the Naive Bayes Classifier benchmark.
'''
class NBC(object):

  ''' 
  Create the Naive Bayes Classifier benchmark instance.
  
  @param dataset - Input dataset to perform NBC on.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, verbose=True): 
    self.verbose = verbose
    self.dataset = dataset

  '''
  Use the shogun libary to implement Naive Bayes Classifier.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def NBCShogun(self, options):
    totalTimer = Timer()
    
    Log.Info("Loading dataset", self.verbose)
    # Load train and test dataset.
    trainData = np.genfromtxt(self.dataset[0], delimiter=',')
    testData = np.genfromtxt(self.dataset[1], delimiter=',')

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

    return totalTimer.ElapsedTime()

  '''
  Perform Naive Bayes Classifier. If the method has been successfully 
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def RunMethod(self, options):
    Log.Info("Perform NBC.", self.verbose)

    if len(self.dataset) != 2:
      Log.Fatal("This method requires two datasets.")
      return -1

    return self.NBCShogun(options)
