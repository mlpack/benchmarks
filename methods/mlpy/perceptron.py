'''
  @file perceptron.py
  @author Marcus Edel

  Perceptron Classifier with mlpy.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
import mlpy

'''
This class implements the Perceptron benchmark.
'''
class MLPY_PERCEPTRON(object):
  def __init__(self, method_param, run_param):
    self.info = "MLPY_PERCEPTRON ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.build_opts = {}
    self.build_opts["alpha"] = 0.1
    if "alpha" in method_param:
      self.build_opts["alpha"] = method_param["alpha"]
    self.build_opts["thr"] = 0.05
    if "threshold" in method_param:
      self.build_opts["thr"] = method_param["threshold"]
    self.build_opts["thr"] = 1000
    if "max_iterations" in method_param:
        self.build_opts["maxiters"] = int(method_param["max_iterations"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = mlpy.Perceptron(**self.build_opts)
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
