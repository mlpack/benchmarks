'''
  @file dtc.py
  Decision Tree Classifier with Milk.
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
from milk.supervised import tree_learner

'''
This class implements the Decision Tree Classifier benchmark.
'''
class DTC(object):

  '''
  Create the Decision Tree Classifier benchmark instance.
  @param dataset - Input dataset to perform DTC on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.model = None
    self.min_split = -1
  '''
  Build the model for the Decision Tree Classifier.
  @param data - The train data.
  @param labels - The labels for the train set.
  @return The created model.
  '''
  def BuildModel(self):
    # Create and train the classifier.
    if self.min_split != -1:
      dtc_learner = tree_learner(min_split=self.min_split)
    else:
      dtc_learner = tree_learner()
    return dtc_learner

  '''
  Use the milk libary to implement the Decision Tree Classifier.
  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def DTCMilk(self, options):
    def RunDTCMilk(q):
      totalTimer = Timer()

      Log.Info("Loading dataset", self.verbose)
      trainData, labels = SplitTrainData(self.dataset)
      testData = LoadDataset(self.dataset[1])

      # Parse options.
      if "minimum_leaf_size" in options:
        self.min_split = options.pop("minimum_leaf_size")
      if len(options) > 0:
        Log.Fatal("Unknown parameters: " + str(options))
        raise Exception("unknown parameters")

      try:
        self.model = self.BuildModel()
        with totalTimer:
          self.model = self.model.train(trainData, labels)
      except Exception as e:
        Log.Debug(e)
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunDTCMilk, self.timeout)

  '''
  Perform the Decision Tree Classifier. If the method has been
  successfully completed return the elapsed time in seconds.
  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform Decision Tree Classifier.", self.verbose)

    results = None
    if len(self.dataset) >= 2:
      results = self.DTCMilk(options)

      if results < 0:
        return results
    else:
      Log.Fatal("This method requires two datasets.")

    # Datastructure to store the results.
    metrics = {'Runtime' : results}
    return metrics
