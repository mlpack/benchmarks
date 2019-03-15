'''
  @file svm.py
  @author Marcus Edel

  Support vector machines with scikit.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from sklearn import svm as ssvm

'''
This class implements the Support vector machines benchmark.
'''
class SCIKIT_SVM(object):
  def __init__(self, method_param, run_param):
    self.info = "SCIKIT_SVM ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.build_opts = {}
    if "kernel" in method_param:
      self.build_opts["kernel"] = str(method_param["kernel"])
    if "c" in method_param:
      self.build_opts["C"] = float(method_param["c"])
    if "gamma" in method_param:
      self.build_opts["gamma"] = float(method_param["gamma"])
    if "degree" in method_param:
      self.build_opts["degree"] = int(method_param["degree"])
    if "cache_size" in method_param:
      self.build_opts["cache_size"] = float(method_param["cache_size"])
    if "max_iterations" in method_param:
      self.build_opts["max_iter"] = int(method_param["max_iterations"])
    if "decision_function_shape" in method_param:
      self.build_opts["decision_function_shape"] = str(
        method_param["decision_function_shape"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = ssvm.SVC(**self.build_opts)
      model.fit(self.data_split[0], self.data_split[1])

      if len(self.data) >= 2:
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
