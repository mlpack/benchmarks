'''
  @file perceptron.py
  @author Anand Soni

  Perceptron Classification with shogun.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from shogun import Perceptron
from shogun import RealFeatures, MulticlassLabels

'''
This class implements the Perceptron benchmark.
'''
class SHOGUN_PERCEPTRON(object):
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_PERCEPTRON ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.iterations = None
    if "max_iterations" in method_param:
      self.iterations = int(method_param["max_iterations"])

    self.train_feat = RealFeatures(self.data_split[0].T)
    self.train_labels = MulticlassLabels(self.data_split[1])
    self.test_feat = RealFeatures(self.data[1].T)

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = Perceptron(self.train_feat, self.train_labels)
      if self.iterations:
        model.set_max_iter(self.iterations)
      model.train()

      if len(self.dataset) == 2:
        predictions = model.apply(self.test_feat)
        predictions = pred.get_labels()

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
