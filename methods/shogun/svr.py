'''
  @file SVR.py
  @author Saurabh Mahindre

  SVR Regression with shogun.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from shogun import RegressionLabels, RealFeatures
from shogun import LibSVR
from shogun import GaussianKernel

'''
This class implements the SVR Regression benchmark.
'''
class SHOGUN_SVR(object):
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_SVR ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.C = 1.0
    if "c" in method_param:
      self.C = float(method_param["c"])
    self.epsilon = 1.0
    if "epsilon" in method_param:
      self.epsilon = float(method_param["epsilon"])
    self.width = 0.1
    if "gamma" in method_param:
      self.width = np.true_divide(1, float(method_param["gamma"]))

    self.train_feat = RealFeatures(self.data_split[0].T)
    self.train_labels = RegressionLabels(self.data_split[1])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      self.kernel = GaussianKernel(self.train_feat, self.train_feat, self.width)

      model = LibSVR(self.C, self.epsilon, self.kernel, self.train_labels)
      model.train()

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
