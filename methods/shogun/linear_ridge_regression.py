'''
  @file linear_ridge_regression.py
  @author Ali Mohamed

  Linear Ridge Regression with shogun.
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
from shogun import LinearRidgeRegression as LRR

'''
This class implements the Linear Ridge Regression benchmark.
'''
class SHOGUN_LINEARRIDGEREGRESSION(object):
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_LINEARRIDGEREGRESSION ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.train_feat = RealFeatures(self.data_split[0].T)
    self.train_labels = RegressionLabels(self.data_split[1])

    if len(self.data) >= 2:
      self.test_feat = RealFeatures(self.data[1].T)

    if "alpha" in method_param:
      self.tau = float(method_param["alpha"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = LRR(self.tau, self.train_feat, self.train_labels)
      model.train()

      if len(self.data) >= 2:
        model.apply_regression(self.test_feat)


    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    if len(self.data) == 3:
      predictions = model.apply_regression(self.test_feat).get_labels()
      metric['MSE'] = Metrics.SimpleMeanSquaredError(self.data[2], predictions)

    return metric
