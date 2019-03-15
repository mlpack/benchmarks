'''
  @file elastic_net.py
  @author Marcus Edel

  Elastic Net Classifier with mlpy.
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
This class implements the Elastic Net Classifier benchmark.
'''
class MLPY_ELASTICNET(object):
  def __init__(self, method_param, run_param):
    self.info = "MLPY_ELASTICNET ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.build_options = {}
    if "rho" in method_param:
      self.build_options['lmb'] = float(method_param["rho"])
    if "alpha" in method_param:
      self.build_options['eps'] = float(method_param["alpha"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = mlpy.ElasticNet(**self.build_options)
      model.learn(self.data_split[0], self.data_split[1])

      if len(self.data) >= 2:
        predictions = model.pred(self.data[1])

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    if len(self.data) == 3:
      metric['MSE'] = Metrics.SimpleMeanSquaredError(self.data[2], predictions)

    return metric
