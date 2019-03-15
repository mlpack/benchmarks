'''
  @file svm.py
  @author Marcus Edel

  Support vector machines with shogun.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from shogun import RealFeatures, MulticlassLabels, LibSVM
from shogun import GaussianKernel, PolyKernel, LinearKernel, SigmoidKernel

'''
This class implements the Support vector machines benchmark.
'''
class SHOGUN_SVM(object):
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_SVM ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.method_param = method_param

    self.train_feat = RealFeatures(self.data_split[0].T)
    self.train_labels = MulticlassLabels(self.data_split[1])

    if len(self.data) >= 3:
      self.test_feat = RealFeatures(self.data[1].T)

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      if "kernel" in self.method_param:
        k = str(self.method_param["kernel"])
      if "c" in self.method_param:
        C = float(self.method_param["c"])
      if "gamma" in self.method_param:
        gamma = float(self.method_param["gamma"])
      if k == "gaussian":
        kernel = GaussianKernel(self.train_feat, self.train_feat, 1)
      elif k == "polynomial":
        if "degree" in self.method_param:
          d = int(self.method_param["degree"])
        else:
          d = 1
        self.kernel = PolyKernel(self.train_feat, self.train_feat, d, True)
      elif k == "linear":
        self.kernel = LinearKernel(self.train_feat, self.train_feat)
      elif k == "hyptan":
        self.kernel = SigmoidKernel(
          self.train_feat, self.train_feat, 2, 1.0, 1.0)
      else:
        self.kernel = GaussianKernel(self.train_feat, self.train_feat, 1)

      model = LibSvm(C, kernel, self.train_labels)
      model.train()

      if len(self.data) >= 3:
        predictions = model.apply_multiclass(self.test_feat).get_labels()

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
