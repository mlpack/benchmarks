'''
  @file perceptron.py
  @author Anand Soni
  @contributor Rukmangadh Sai Myana

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
from shogun import RealFeatures, BinaryLabels
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
This class implements the Perceptron benchmark for binary classification.

Notes
-----
The following are the configurable options available for this benchmark:
* max-iterations: The maximum number of iterations.
* learing-rate: The learning rate.
* bias: The bias in the linear decision boundary expression
* initialize-hyperplane: whether to initialize hyperplane or not
* solver: "auto", "cplex", "glpk", "newton", "direct", "elasticnet", 
"block_norm"
'''
class SHOGUN_PERCEPTRON(object):

  '''
  Create the Perceptron Classification benchmark instance.
  
  @type method_param - dict
  @param method_param - Extra options for the benchmarking method.
  @type run_param - dict
  @param run_param - Path option for executing the benckmark. Not used for 
  Shogun.
  '''
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_PERCEPTRON ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.train_feat = RealFeatures(self.data_split[0].T)

	# Encode the labels into {-1 , +1}
    self.train_labels, self.label_map = label_encoder(
      self.data_split[1], "binary")
    self.train_labels = BinaryLabels(self.train_labels)

    if len(self.data) >= 2:
      self.test_feat = RealFeatures(self.data[1].T)

    self.max_iter = None
    if "max-iterations" in method_param:
      self.max_iter = int(method_param["max-iterations"])

    self.learn_rate = None
    if "learning-rate" in method_param:
      self.learn_rate = float(method_param["learning-rate"])

    self.bias = None
    if "bias" in method_param:
      self.bias = float(method_param["bias"])

    self.init_hyperplane = None
    if "initialize-hyperplane" in method_param:
      self.init_hyperplane = bool(method_param["initialize-hyperplane"])

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
      model = Perceptron(self.train_feat, self.train_labels)

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

      if self.max_iter:
        model.set_max_iter(self.max_iter)

      if self.learn_rate:
        model.set_learn_rate(self.learn_rate)

      if self.bias:
        model.set_bias(self.bias)

      if self.init_hyperplane:
        model.set_initialize_hyperplane(self.init_hyperplane)

      model.train()

      if len(self.data) >= 2:
        predictions = model.apply(self.test_feat).get_labels()

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    if len(self.data) >= 2:
      predictions = label_decoder(predictions, self.label_map)

    if len(self.data) >= 3:
      confusionMatrix = Metrics.ConfusionMatrix(self.data[2], predictions)
      metric['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metric['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metric['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metric['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metric['MSE'] = Metrics.SimpleMeanSquaredError(self.data[2], predictions)

    return metric
