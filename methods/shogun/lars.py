'''
  @file lars.py
  @author Marcus Edel
  @contributor Rukmangadh Sai Myana

  Least Angle Regression with shogun.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from shogun import RegressionLabels, RealFeatures, NormOne, PruneVarSubMean
from shogun import LeastAngleRegression
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
This class implements the Least Angle Regression benchmark for regression.

Notes
-----
The following are the configurable options available for this benchmark:
* lasso: True(LARS in LASSO mode), False(LARS in stage-wise mode)
* solver: "auto", "cplex", "glpk", "newton", "direct", "elasticnet", 
"block_norm"

The Shogun Library doesn't give us a seperate class for LASSO regression. LASSO
is performed with LARS in LASSO mode.
'''
class SHOGUN_LARS(object):

  '''
  Create the Least Angle Regression benchmark instance.

  @type method_param - dict
  @param method_param - Extra options for the benchmarking method.
  @type run_param - dict
  @param run_param - Path option for executing the benchmark. Not used for
  Shogun.
  '''
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_LARS ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.train_features = RealFeatures(self.data_split[0].T)
    self.train_labels = RegressionLabels(self.data_split[1])

    if len(self.data) >= 2:
      self.test_features = RealFeatures(self.data[1].T)

    self.lasso = True
    if "lasso" in method_param:
      self.lasso = bool(method_param["lasso"])

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

      # Mean Normalize 'X' and Center 'Y'
      SubtractMean = PruneVarSubMean()
      Normalize = NormOne()

      SubtractMean.init(self.train_features)
      transformed_train_features = SubtractMean.apply(self.train_features)

      if len(self.data) >= 2:
        transformed_test_features = SubtractMean.apply(self.test_features)

      Normalize.init(transformed_train_features)
      preprocessed_train_features = Normalize.apply(transformed_train_features)

      if len(self.data) >= 2:
        preprocessed_test_features = Normalize.apply(transformed_test_features)

      model = LeastAngleRegression(self.lasso)

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

      model.set_labels(self.train_labels)
      model.train(preprocessed_train_features)

      if len(self.data) >= 2:
        predictions = model.apply(preprocessed_test_features).get_labels()

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    if len(self.data) >= 3:
      confusionMatrix = Metrics.ConfusionMatrix(self.data[2], predictions)
      metric['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metric['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metric['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metric['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metric['MSE'] = Metrics.SimpleMeanSquaredError(self.data[2], predictions)

    return metric
