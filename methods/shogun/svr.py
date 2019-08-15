'''
  @file SVR.py
  @author Saurabh Mahindre
  @contributor Rukmangadh Sai Myana

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
from shogun import (
  GaussianKernel, 
  PolyKernel, 
  LinearKernel, 
  SigmoidKernel,
  PowerKernel,
  LogKernel,
  CauchyKernel,
  ConstKernel,
  DiagKernel,
  )

from shogun import (
  EuclideanDistance,
  BrayCurtisDistance,
  ChiSquareDistance,
  MahalanobisDistance,
  CosineDistance,
  TanimotoDistance,
  MinkowskiMetric,
  JensenMetric,
  ChebyshewMetric,
  CanberraMetric,
  GeodesicMetric
  )

from shogun import LIBSVR_EPSILON_SVR, LIBSVR_NU_SVR

'''
This class implements the Support Vector Regression benchmark for regression.

Notes
-----

'''
class SHOGUN_SVR(object):

  '''
  Create the Support Vector Machine benchmark instance.
  
  @type method_param - dict
  @param method_param - Extra options for the benchmarking method.
  @type run_param - dict
  @param run_param - Path option for executing the benckmark. Not used for 
  Shogun.
  '''
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_SVR ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.train_feat = RealFeatures(self.data_split[0].T)
    self.train_labels = RegressionLabels(self.data_split[1])

    if len(self.data) >= 2:
      self.test_feat = RealFeatures(self.data[1].T)

    self.solver_type = "epsilon"
    if "libsvr-solver" in method_param:
      self.solver_type = str(method_param["libsvr-solver"])

    self.C = 1.0
    if "C" in method_param:
      self.C = float(method_param["C"])

    self.svr_param = 1.0
    if "svr-paramter" in method_param:
      self.svr_param = float(method_param["svr-parameter"])

    self.kernel = "Gaussian"
    if "kernel" in method_param:
      self.kernel = str(method_param["kernel"])

    self.degree = 3
    if "degree" in method_param:
      self.degree = int(method_param["degree"])

    self.gamma = 2.0
    if "gamma" in method_param:
      self.gamma = float(method_param["gamma"])

    self.distance = "Euclidean"
    if "distance" in method_param:
      self.distance = str(method_param["distance"])

    self.cache_size = 10
    if "cache-size" in method_param:
      cache_size = int(method_param["cache-size"])

    self.coef0 = 1.0
    if "coef0" in method_param:
      self.coef0 = float(method_param["coef0"])

    self.order = 2.0
    if "order" in method_param:
      self.order = float(method_param["order"])

    self.width = 2.0
    if "width" in method_param:
      self.width = float(method_param["width"])

    self.sigma = 1.5
    if "sigma" in method_param:
      self.sigma = float(method_param["sigma"])

    self.const = 2.0
    if "constant" in method_param:
      const = float(method_param["constant"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:

      if self.distance == "Euclidean":
        distanceMethod = EuclideanDistance()

      elif self.distance == "Bray-Curtis":
        distanceMethod = BrayCurtisDistance()

      elif self.distance == "Chi-Square":
        distanceMethod = ChiSquareDistance()

      elif self.distance == "MahalanobisDistance":
        distanceMethod = MahalanobisDistance()

      elif self.distance == "Cosine":
        distanceMethod = CosineDistance()

      elif self.distance == "Tanimoto":
        distanceMethod = TanimotoDistance()

      elif self.distance == "Minkowski":
        distanceMethod = MinkowskiMetric()

      elif self.distance == "Jensen":
        distanceMethod = JensenMetric()

      elif self.distance == "Chebyshev":
        distanceMethod = ChebyshewMetric()

      elif self.distance == "Canberra":
        distanceMethod = CanberraMetric()

      elif self.distance == "Geodesic":
        distanceMethod = GeodesicMetric()

      else:
        raise ValueError("Provided distance is not supported by benchmark")

      if self.kernel == "Polynomial":
        kernelMethod = PolyKernel(self.train_feat, self.train_feat, self.degree, 
          True, self.cache_size)

      elif self.kernel == "Gaussian":
        kernelMethod = GaussianKernel(self.train_feat, self.train_feat, 
          self.width, self.cache_size)

      elif self.kernel == "Linear":
        kernelMethod = LinearKernel(self.train_feat, self.train_feat)

      elif self.kernel == "Hyptan" or self.kernel == "Sigmoid":
        kernelMethod = SigmoidKernel(self.train_feat, self.train_feat, 
          self.cache_size, self.gamma, self.coef0)

      elif self.kernel == "Power":
        kernelMethod = PowerKernel(self.train_feat, self.train_feat, 
          self.degree, distanceMethod)

      elif self.kernel == "Log":
        kernelMethod = LogKernel(self.train_feat, self.train_feat, self.degree,
          distanceMethod)

      elif self.kernel == "Cauchy":
        kernelMethod = CauchyKernel(self.train_feat, self.train_feat, 
          self.sigma, distanceMethod)

      elif self.kernel == "Constant":
        kernelMethod = ConstKernel(self.train_feat, self.train_feat, self.const)

      elif self.kernel == "Diagonal":
        kernelMethod = DiagKernel(self.train_feat, self.train_feat, self.const)

      else:
        raise ValueError("Provided Kernel not supported by current benchmark")

      if self.solver_type == "epsilon":
        model = LibSVR(self.C, self.svr_param, kernelMethod, 
          self.train_labels, LIBSVR_EPSILON_SVR)

      elif self.solver_type == "nu":
        model = LibSVR(self.C, self.svr_param, kernelMethod, 
          self.train_labels, LIBSVR_NU_SVR)

      else:
        raise ValueError("Unknown solver type")

      model.train()

      if len(self.data) >= 2:
        predictions = model.apply(self.test_feat).get_labels()

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    if len(self.data) >= 3:
      metric['MSE'] = Metrics.SimpleMeanSquaredError(self.data[2], predictions)

    return metric
