'''
  @file random_forest.py

  Classifier implementing the Random Forest classifier with shogun.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from shogun import RealFeatures, MulticlassLabels, RandomForest
from shogun import EuclideanDistance, MajorityVote

'''
This class implements the decision trees benchmark.
'''
class SHOGUN_RANDOMFOREST(object):
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_RANDOMFOREST ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    if "num_trees" in method_param:
      self.numTrees = int(method_param["num_trees"])

    self.form = 1
    if "dimensions" in method_param:
      self.form = int(method_param["dimensions"])

    self.train_feat = RealFeatures(self.data_split[0].T)
    self.train_labels = MulticlassLabels(self.data_split[1])

    if len(self.data) >= 2:
      self.test_feat = RealFeatures(self.data[1].T)

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      mVote = MajorityVote()
      model = RandomForest(self.form, self.numTrees)
      model.set_combination_rule(mVote)
      model.set_labels(self.train_labels)
      model.train(self.train_feat)

      if len(self.data) >= 2:
        predictions =  model.apply_multiclass(self.test_feat).get_labels()

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    if len(self.data) >= 3:
      confusionMatrix = Metrics.ConfusionMatrix(self.data[2], predictions)
      metric['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metric['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metric['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metric['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metric['MSE'] = Metrics.SimpleMeanSquaredError(self.data[2], predictions)

    return metric
