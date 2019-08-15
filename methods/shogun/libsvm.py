'''
  @file libsvm.py
  @author Marcus Edel
  @contributor Rukmangadh Sai Myana

  Support vector machine classification with shogun using LIBSVM
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from shogun import RealFeatures, MulticlassLabels
from shogun import MulticlassLibSVM as MC_LSVM
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
  ManhattanMetric,
  JensenMetric,
  ChebyshewMetric,
  CanberraMetric,
  GeodesicMetric
  )

from shogun import LIBSVM_C_SVC, LIBSVM_NU_SVC

'''
This class implements the Support vector machines benchmark for multi-class
classification.

Notes
-----
The following are the configurable options available for this benchmark:
* C:
* nu: The 'nu' used in nu-svc
* kernel: "Gaussian", "Polynomial", "Linear", "Sigmoid", "Power",
"Log", "Cauchy", "Constant", "Diagonal"

Each kernel might have it's own seperate set of additional options. Check the
Shogun Library's documentation for these. Most of these additional options are
configurable for this benchmark.
'''
class SHOGUN_LIBSVM(object):

  '''
  Create the Support Vector Machine Classifier benchmark instance.
  
  @type method_param - dict
  @param method_param - Extra options for the benchmarking method.
  @type run_param - dict
  @param run_param - Path option for executing the benckmark. Not used for 
  Shogun.
  '''
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_LIBSVM ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.train_feat = RealFeatures(self.data_split[0].T)

    # Encode the labels into {0,1,2,3,......,num_classes-1}
    self.train_labels, self.label_map = label_encoder(self.data_split[1])
    self.train_labels = MulticlassLabels(self.train_labels)

    if len(self.data) >= 2:
      self.test_feat = RealFeatures(self.data[1].T)

    self.C = 1.0
    if "C" in method_param:
      self.C = float(method_param["C"])

    self.nu = 0.5
    if "nu" in method_param:
      self.nu = float(method_param["nu"])

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

      elif self.distance == "Manhattan":
        distanceMethod = ManhattanMetric()

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
        kernelMethod = PolyKernel(self.train_feat, self.train_feat, self.degree, True,
            self.cache_size)

      elif self.kernel == "Gaussian":
        kernelMethod = GaussianKernel(self.train_feat, self.train_feat, self.width,
            self.cache_size)

      elif self.kernel == "Linear":
        kernelMethod = LinearKernel(self.train_feat, self.train_feat)

      elif self.kernel == "Hyptan" or self.kernel == "Sigmoid":
        kernelMethod = SigmoidKernel(self.train_feat, self.train_feat, self.cache_size,
            self.gamma, self.coef0)

      elif self.kernel == "Power":
        kernelMethod = PowerKernel(self.train_feat, self.train_feat, self.degree,
          distanceMethod)

      elif self.kernel == "Log":
        kernelMethod = LogKernel(self.train_feat, self.train_feat, self.degree,
            distanceMethod)

      elif self.kernel == "Cauchy":
        kernelMethod = CauchyKernel(self.train_feat, self.train_feat, self.sigma,
            distanceMethod)

      elif self.kernel == "Constant":
        kernelMethod = ConstKernel(self.train_feat, self.train_feat, self.const)

      elif self.kernel == "Diagonal":
        kernelMethod = DiagKernel(self.train_feat, self.train_feat, self.const)

      else:
        raise ValueError("Provided Kernel not supported by current benchmark")

      model = MC_LSVM(self.C, kernelMethod, self.train_labels)
      model.train()

      if len(self.data) >= 2:
        predictions = model.apply_multiclass(self.test_feat).get_labels()

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    if len(self.data) >= 2:
      predictions = label_decoder(predictions, self.label_map)

    if len(self.data) == 3:
      confusionMatrix = Metrics.ConfusionMatrix(self.data[2], predictions)
      metric['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metric['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metric['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metric['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metric['MSE'] = Metrics.SimpleMeanSquaredError(self.data[2], predictions)

    return metric
