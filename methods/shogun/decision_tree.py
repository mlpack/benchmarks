'''
  @file decision_tree.py
  @author Saurabh Mahindre

  Classifier implementing the CART (decision tree) classifier with shogun.
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
from modshogun import RealFeatures, MulticlassLabels, CARTree, EuclideanDistance

'''
This class implements the decision tree benchmark.
'''
class DTC(object):

  '''
  Create the CARTree Classifier benchmark instance.
  @param dataset - Input dataset.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.model = None

  '''
  Build the model for the CARTree Classifier.
  @param data - The train data.
  @param labels - The labels for the train set.
  @return The created model.
  '''
  def BuildModel(self, data, labels, options):
    cart = CARTree()
    cart.set_feature_types(np.array([False] * data.get_num_features()))
    cart.set_labels(labels)
    cart.train(data)

    return cart

  '''
  Use the shogun libary to implement the CARTree Classifier.
  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def DTCShogun(self, options):
    def RunDTCShogun(q):
      totalTimer = Timer()

      Log.Info("Loading dataset", self.verbose)
      trainData, labels = SplitTrainData(self.dataset)
      trainData = RealFeatures(trainData.T)
      labels = MulticlassLabels(labels)
      testData = RealFeatures(LoadDataset(self.dataset[1]).T)

      if len(options) > 0:
        Log.Fatal("Unknown parameters: " + str(options))
        raise Exception("unknown parameters")

      try:
        with totalTimer:
          self.model = self.BuildModel(trainData, labels, options)
          # Run the CARTree Classifier on the test dataset.
          self.model.apply_multiclass(testData).get_labels()
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)

      return time

    return timeout(RunDTCShogun, self.timeout)

  '''
  Perform the classification using CARTree. If the method has been
  successfully completed return the elapsed time in seconds.
  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''

  def RunMetrics(self, options):
    Log.Info("Perform DTC.", self.verbose)

    results = None
    if len(self.dataset) >= 2:
        results = self.DTCShogun(options)
    else:
      Log.Fatal("This method requires at least two datasets.")

    return {'Runtime' : results}
