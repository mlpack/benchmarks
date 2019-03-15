'''
  @file dtc.py
  @author Marcus Edel

  Decision Tree Classifier with scikit.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from sklearn.tree import DecisionTreeClassifier

'''
This class implements the Decision Tree Classifier benchmark.
'''
class SCIKIT_DTC(object):
  def __init__(self, method_param, run_param):
    self.info = "SCIKIT_DTC ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.build_opts = {}
    if "fitness_function" in method_param:
      self.build_opts["criterion"] = str(method_param["criterion"])
    if "max_depth" in method_param:
      self.build_opts["max_depth"] = int(method_param["max_depth"])
    if "split_strategy" in method_param:
      self.build_opts["splitter"] = str(method_param["split_strategy"])
    if "minimum_samples_split" in method_param:
      self.build_opts["min_samples_split"] = int(
        method_param["minimum_samples_split"])
    if "minimum_leaf_size" in method_param:
      self.build_opts["min_samples_leaf"] = int(
        method_param["minimum_leaf_size"])
    if "max_features" in method_param:
      self.build_opts["max_features"] = int(method_param["max_features"])
    if "max_leaf_nodes" in method_param:
      self.build_opts["max_leaf_nodes"] = int(method_param["max_leaf_nodes"])
    if "seed" in method_param:
      self.build_opts["random_state"] = int(method_param["seed"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = DecisionTreeClassifier(**self.build_opts)
      model.fit(self.data_split[0], self.data_split[1])
      predictions = model.predict(self.data[1])

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    if len(self.data) == 3:
      confusionMatrix = Metrics.ConfusionMatrix(self.data[2], predictions)
      metric['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metric['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metric['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metric['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metric['MSE'] = Metrics.SimpleMeanSquaredError(self.data[2], predictions)

    return metric
