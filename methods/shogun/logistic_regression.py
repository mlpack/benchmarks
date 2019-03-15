'''
  @file logistic_regression.py
  @author Marcus Edel

  Logistic Regression with shogun.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from shogun import RealFeatures, MulticlassLabels
from shogun import MulticlassLogisticRegression

'''
This class implements the Logistic Regression benchmark.
'''
class SHOGUN_LOGISTICREGRESSION(object):
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_LOGISTICREGRESSION ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.train_feat = RealFeatures(self.data_split[0].T)
    self.train_labels = MulticlassLabels(self.data_split[1])

    if len(self.data) >= 2:
      self.test_feat = RealFeatures(self.data[1].T)

    self.max_iter = None
    if "max_iterations" in method_param:
      self.max_iter = int(method_param["max_iterations"])
    self.z = 1
    if "lambda" in method_param:
      self.z = float(method_param["lambda"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = MulticlassLogisticRegression(self.z, self.train_feat,
        self.train_labels)

      if self.max_iter is not None:
        model.set_max_iter(self.max_iter);

      model.train()

      if len(self.data) >= 2:
        predictions = model.apply(self.test_feat).get_labels()

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
