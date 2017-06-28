'''
  @file random_forest.py

  Classifier implementing the Random Forest classifier with shogun.
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
from modshogun import RealFeatures, MulticlassLabels, RandomForest, EuclideanDistance, MajorityVote

'''
This class implements the decision trees benchmark.
'''
class RANDOMFOREST(object):

  '''
  Create the Random Forest Classifier benchmark instance.
  @param dataset - Input dataset.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.model = None
    self.form = 1
    self.numTrees = 10

  '''
  Build the model for the Random Forest Classifier.
  @param data - The train data.
  @param labels - The labels for the train set.
  @return The created model.
  '''
  def BuildModel(self, data, labels, options):
    mVote = MajorityVote()
    randomForest = RandomForest(self.form,self.numTrees)
    randomForest.set_combination_rule(mVote)
    randomForest.set_labels(labels)
    randomForest.train(data)

    return randomForest

  '''
  Use the shogun libary to implement the Random Forest Classifier.
  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RandomForestShogun(self, options):
    def RunRandomForestShogun(q):
      totalTimer = Timer()

      Log.Info("Loading dataset", self.verbose)
      trainData, labels = SplitTrainData(self.dataset)
      trainData = RealFeatures(trainData.T)
      labels = MulticlassLabels(labels)
      testData = RealFeatures(LoadDataset(self.dataset[1]).T)

      if "num_trees" in options:
        self.numTrees = int(options.pop("num_trees"))
      else:
        Log.Fatal("Required parameter 'num_trees' not specified!")
        raise Exception("missing parameter")

      self.form = 1
      if "dimensions" in options:
        self.form = int(options.pop("dimensions"))

      if len(options) > 0:
        Log.Fatal("Unknown parameters: " + str(options))
        raise Exception("unknown parameters")

      try:
        with totalTimer:
          self.model = self.BuildModel(trainData, labels, options)
          # Run the Random Forest Classifier on the test dataset.
          self.model.apply_multiclass(testData).get_labels()
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunRandomForestShogun, self.timeout)

  '''
  Perform the classification using Random Forest. If the method has been
  successfully completed return the elapsed time in seconds.
  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform Random Forest.", self.verbose)

    if len(self.dataset) >= 2:
        results = self.RandomForestShogun(options)
    else:
      Log.Fatal("This method requires at least two datasets.")

    return {'Runtime' : results}
