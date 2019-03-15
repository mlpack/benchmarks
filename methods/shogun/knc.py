'''
  @file knc.py
  @author Marcus Edel

  Classifier implementing the k-nearest neighbors vote with shogun.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from shogun import RealFeatures, MulticlassLabels, KNN, EuclideanDistance
from shogun import KNN_KDTREE

'''
This class implements the Support vector machines benchmark.
'''
class SHOGUN_KNC(object):
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_KNC ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.build_opts = {}
    if "k" in method_param:
      self.build_opts["n_neighbors"] = int(method_param["k"])

  def __str__(self):
    return self.info

  def metric(self):
    train_data = RealFeatures(self.data_split[0].T)
    labels = MulticlassLabels(self.data_split[1])
    test_data = RealFeatures(self.data[1].T)


    totalTimer = Timer()
    with totalTimer:
      distance = EuclideanDistance(self.data_split[0], self.data_split[0])
      model = KNN(self.build_opts["n_neighbors"], distance, self.data_split[1],
        KNN_KDTREE)
      model.train()

      self.predictions = model.apply_multiclass(test_data).get_labels()

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
