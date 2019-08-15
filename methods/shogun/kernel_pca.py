'''
  @file kernel_pca.py
  @author Marcus Edel
  @contributor Rukmangadh Sai Myana

  Kernel Principal Components Analysis with shogun.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from shogun import RealFeatures, KernelPCA
from shogun import (
  GaussianKernel,
  PolyKernel,
  LinearKernel,
  SigmoidKernel,
  BesselKernel,
  PowerKernel,
  LogKernel,
  CauchyKernel,
  ConstKernel,
  DiagKernel
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

'''
This class implements the Kernel Principal Components Analysis benchmark.

Notes
-----
The following are the configurable options available for this benchmark:
* target-dimensions: The new dimensions/dimensionality of samples in dataset.
* kernel: "Gaussian", "Polynomial", "Linear", "Sigmoid", "Bessel", "Power",
"Log", "Cauchy", "Constant", "Diagonal"

Each kernel might have it's own seperate set of additional options. Check the
Shogun Library's documentation for these. Most of these additional options are
configurable for this benchmark.
'''
class SHOGUN_KPCA(object):
  '''
  Create the Kernel Principal Component Analysis benchmark instance.

  @type method_param - dict
  @param method_param - Extra options for the benchmarking method.
  @type run_param - dict
  @param run_param - Path option for executing the benchmark. Not used for
  Shogun.
  '''
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_KPCA ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])

    self.kernel = "Gaussian"
    if "kernel" in method_param:
      self.kernel = str(method_param["kernel"])

    self.d = self.data[0].shape[1]
    if "target-dimensions" in method_param:
      self.d = int(method_param["target-dimensions"])

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
  @returns - Information as a single string
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
      data_feat = RealFeatures(self.data[0].T)

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
        kernelMethod = PolyKernel(data_feat, data_feat, self.degree, True,
            self.cache_size)

      elif self.kernel == "Gaussian":
        kernelMethod = GaussianKernel(data_feat, data_feat, self.width,
            self.cache_size)

      elif self.kernel == "Linear":
        kernelMethod = LinearKernel(data_feat, data_feat)

      elif self.kernel == "Hyptan" or self.kernel == "Sigmoid":
        kernelMethod = SigmoidKernel(data_feat, data_feat, self.cache_size,
            self.gamma, self.coef0)

      elif self.kernel == "Bessel":
        kernelMethod = BesselKernel(data_feat, data_feat, self.order,
          self.width, self.degree, distanceMethod, self.cache_size)

      elif self.kernel == "Power":
        kernelMethod = PowerKernel(data_feat, data_feat, self.degree,
          distanceMethod)

      elif self.kernel == "Log":
        kernelMethod = LogKernel(data_feat, data_feat, self.degree,
            distanceMethod)

      elif self.kernel == "Cauchy":
        kernelMethod = CauchyKernel(data_feat, data_feat, self.sigma,
            distanceMethod)

      elif self.kernel == "Constant":
        kernelMethod = ConstKernel(data_feat, data_feat, self.const)

      elif self.kernel == "Diagonal":
        kernelMethod = DiagKernel(data_feat, data_feat, self.const)
      else:
        raise ValueError("Provided Kernel not supported by current benchmark")

      model = KernelPCA(kernelMethod)
      model.set_target_dim(self.d)
      model.init(data_feat)
      model.apply_to_feature_matrix(data_feat)

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
