'''
  @file svm.py
  @author Marcus Edel

  Support vector machines with mlpy.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from mlpy import LibSvm

'''
This class implements the Support vector machines benchmark.
'''
class MLPY_SVM(object):
  def __init__(self, method_param, run_param):
    self.info = "MLPY_SVM ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.build_opts = {}
    if "kernel" in method_param:
      self.build_opts["kernel_type"] = method_param["kernel"]
    else:
      self.build_opts["kernel_type"] = 'rbf'
    if "c" in method_param:
      self.build_opts["C"] = float(method_param["c"])
    else:
      self.build_opts["C"] = 1.0
    if "gamma" in method_param:
      self.build_opts["gamma"] = float(method_param["gamma"])
    else:
      self.build_opts["gamma"] = 0.0

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = LibSvm(**self.build_opts)
      model.learn(self.data_split[0], self.data_split[1])

      if len(self.data) >= 2:
        predictions = model.pred(self.data[1])

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
