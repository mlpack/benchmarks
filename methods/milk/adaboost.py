'''
  @file adaboost.py
  AdaBoost classifier with Milk.
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
import milk.supervised.tree
import milk.supervised.adaboost
from milk.supervised.multi import one_against_one
'''
This class implements the AdaBoost classifier benchmark.
'''
class ADABOOST(object):

  '''
  Create the AdaBoost classifier benchmark instance.
  @param dataset - Input dataset to perform ADABOOST on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.model = None

  '''
  Build the model for the AdaBoost classifier.
  @param data - The train data.
  @param labels - The labels for the train set.
  @return The created model.
  '''
  def BuildModel(self):
    # Create and train the classifier.
    weak = milk.supervised.tree.stump_learner()
    learner = milk.supervised.adaboost.boost_learner(weak)
    learner = one_against_one(learner)
    return learner

  '''
  Use the milk libary to implement the AdaBoost classifier.
  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def ADABOOSTMilk(self, options):
    def RunADABOOSTMilk(q):
      totalTimer = Timer()

      Log.Info("Loading dataset", self.verbose)
      trainData, labels = SplitTrainData(self.dataset)
      testData = LoadDataset(self.dataset[1])

      try:
        self.model = self.BuildModel()
        with totalTimer:
         self.model = self.model.train(trainData, labels)
          
      except Exception as e:
        Log.Debug(str(e))
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)

      return time

    return timeout(RunADABOOSTMilk, self.timeout)

  '''
  Perform the AdaBoost classifier. If the method has been
  successfully completed return the elapsed time in seconds.
  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform ADABOOST.", self.verbose)

    # No extra options allowed.
    if len(options) > 0:
      Log.Fatal("Unknown parameters: " + str(options))
      raise Exception("unknown parameters")

    results = None
    if len(self.dataset) >= 2:
      results = self.ADABOOSTMilk(options)

      if results < 0:
        return results
    else:
      Log.Fatal("This method requires two datasets.")

    # Datastructure to store the results.
    metrics = {'Runtime' : results}
    return metrics
