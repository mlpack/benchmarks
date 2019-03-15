'''
  @file decision_tree.py
  @author Saurabh Mahindre
  Classifier implementing the CART (decision tree) classifier with shogun.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from shogun import RealFeatures, MulticlassLabels, CARTree, EuclideanDistance

'''
This class implements the decision tree benchmark.
'''
class SHOGUN_DTC(object):
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_DTC ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.build_opts = {}
    if "algorithm" in method_param:
      self.build_opts["solver"] = str(method_param["algorithm"])
    if "epsilon" in method_param:
      self.build_opts["epsilon"] = float(method_param["epsilon"])
    if "max_iterations" in method_param:
      self.build_opts["max_iter"] = int(method_param["max_iterations"])

    self.train_feat = RealFeatures(self.data_split[0].T)
    self.train_labels = MulticlassLabels(self.data_split[1])
    self.test_feat = RealFeatures(self.data[1].T)

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = CARTree()
      model.set_feature_types(np.array([False] *
        self.train_feat.get_num_features()))
      model.set_labels(self.train_labels)
      model.train(self.train_feat)

      predictions = model.apply_multiclass(self.test_feat).get_labels()

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
