'''
  @file linear_regression.py
  @author Marcus Edel
  @contributor Rukmangadh Sai Myana

  Linear Regression with shogun.
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
from shogun import LeastSquaresRegression
from shogun import (
  ST_AUTO,
  ST_CPLEX,
  ST_GLPK,
  ST_NEWTON,
  ST_DIRECT,
  ST_ELASTICNET,
  ST_BLOCK_NORM
  )

'''
This class implements the Linear Regression benchmark for regression.

Notes
-----
The following configurable options are available for this benchmark:
* bias: The bias in the linear hypothesis expression.
* solver: "auto", "cplex", "glpk", "newton", "direct", "elasticnet",
"block_norm"
'''
class SHOGUN_LINEARREGRESSION(object):
  '''
  Create the Linear Regression benchmark instance.

  @type method_param - dict
  @param method_param - Extra options for the benchmarking method.
  @type run_param - dict
  @param run_param - Path option for executing the benckmark. Not used for 
  Shogun.
  '''
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_LINEARREGRESSION ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.train_feat = RealFeatures(self.data_split[0].T)
    self.train_labels = RegressionLabels(self.data_split[1])

    if len(self.data) >= 2:
      self.test_feat = RealFeatures(self.data[1].T)

    self.bias = 0
    if "bias" in method_param:
      self.bias = float(method_param["bias"])

    self.solver = "auto"
    if "solver" in method_param:
      self.solver = str(method_param["solver"])

  '''
  Return information about the benchmarking instance.

  @rtype - str
  @returns - Information as a single string.
  '''
  def __str__(self):
    return self.info

  '''
  Calculate metrics to be used for benchmarking.

  @rtype - dict
  @returns - Evaluated metrics.
  '''
  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = LeastSquaresRegression(self.train_feat, self.train_labels)

      model.set_bias(self.bias)

      if self.solver == "auto":
        model.set_solver_type(ST_AUTO)

      elif self.solver == "cplex":
        model.set_solver_type(ST_CPLEX)

      elif self.solver == "glpk":
        model.set_solver_type(ST_GLPK)

      elif self.solver == "newton":
        model.set_solver_type(ST_NEWTON)

      elif self.solver == "direct":
        model.set_solver_type(ST_DIRECT)

      elif self.solver == "elasticnet":
        model.set_solver_type(ST_ELASTICNET)

      elif self.solver == "block_norm":
        model.set_solver_type(ST_BLOCK_NORM)

      else:
        raise ValueError("Provided solver not supported by current benchmark")

      model.train()

      if len(self.data) >= 2:
        predictions = model.apply(self.test_feat)
        predictions = predictions.get_labels()

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    if len(self.data) == 3:
      metric['MSE'] = Metrics.SimpleMeanSquaredError(self.data[2], predictions)

    return metric
