'''
  @file lasso.py
  @author Youssef Emad El-Din

  Lasso Regression with shogun.
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
from shogun import LeastAngleRegression

'''
This class implements the Lasso Regression benchmark.
'''
class SHOGUN_LASSO(object):
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_LASSO ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.method_param = method_param

    self.lambda1 = None
    if "lambda1" in method_param:
      self.lambda1 = float(method_param["lambda1"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = LeastAngleRegression(lasso=True)

      if self.lambda1:
        model.set_max_l1_norm(self.lambda1)

      model.set_labels(RegressionLabels(self.data_split[1]))
      model.train(RealFeatures(self.data_split[0].T))

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
