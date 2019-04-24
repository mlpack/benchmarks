'''
  @file gpc.py
  @author Rukmangadh Sai Myana

  Gaussian Process Classification with shogun
'''

import os
import sys
import inspect

# Import the util path, this method even works if the path contains symlinks to 
# modules
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *

from shogun import RealFeatures, MulticlassLabels
from shogun import (
  GaussianKernel, 
  PolyKernel, 
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
  ChiSquareDistance,
  TanimotoDistance,
  MinkowskiMetric,
  ManhattanMetric,
  JensenMetric,
  CanberraMetric,
  )
from shogun import MultiLaplaceInferenceMethod
from shogun import SoftMaxLikelihood
from shogun import GaussianProcessClassification as SGPC
from shogun import ConstMean

'''
This class implements the Gaussian Process Classification benchmark for
Multi-class classification.

Notes
-----
The following are the configurable options available for this benchmark:
* kernel: "Gaussian", "Polynomial", "Sigmoid", "Bessel", "Power", "Log", 
"Cauchy", "Constant", "Diagonal"

Each kernel might have it's own separate set of additional options. Check the 
Shogun Library's documentation for these. Most of these additional options are 
configurable for this benchmark.
'''
class SHOGUN_GPC(object):

  '''
  Create the Gaussian Process Classification benchmark instance.
  
  @type method_param - dict
  @param method_param - Extra options for the benchmarking method.
  @type run_param - dict
  @param run_param - Path option for executing the benckmark. Not used for 
  Shogun.
  '''
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_GPC (" + str(method_param) + ")"

    #Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.train_features = RealFeatures(self.data_split[0].T)

	# Encode the labels into {0,1,2,3,......,num_classes-1}
    self.train_labels, self.label_map = label_encoder(self.data_split[1])
    self.train_labels = MulticlassLabels(self.train_labels)

    if len(self.data) >= 2:
      self.test_features = RealFeatures(self.data[1].T)

    self.method_param = method_param

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

    distance = "Euclidean"
    if "distance" in self.method_param:
      distance = str(self.method_param["distance"])

    kernel = "Gaussian"
    if "kernel" in self.method_param:
      kernel = str(self.method_param["kernel"])

    cache_size = 10
    if "cache-size" in self.method_param:
      cache_size = int(self.method_param["cache-size"])

    degree = 2
    if "degree" in self.method_param:
      degree = int(self.method_param["degree"])

    gamma = 2.0
    if "gamma" in self.method_param:
      gamma = float(self.method_param["gamma"])

    coef0 = 1.0
    if "coef0" in self.method_param:
      coef0 = float(self.method_param["coef0"])

    order = 2.0
    if "order" in self.method_param:
      order = float(self.method_param["order"])

    width = 2.0
    if "width" in self.method_param:
      width = float(self.method_param["order"])

    sigma = 1.5
    if "sigma" in self.method_param:
      sigma = float(self.method_param["sigma"])

    const = 2.0
    if "constant" in self.method_param:
      const = float(self.method_param["constant"])

    #Choosing a Distance Function required by some Kernels
    if distance=="Euclidean":
      distanceMethod = EuclideanDistance()

    elif distance=="Chi-Square":
      distanceMethod = ChiSquareDistance()

    elif distance=="Tanimoto":
      distanceMethod = TanimotoDistance()

    elif distance=="Minkowski":
      distanceMethod = MinkowskiMetric()

    elif distance=="Manhattan":
      distanceMethod = ManhattanMetric()

    elif distance=="Jensen":
      distanceMethod = JensenMetric()

    elif distance=="Canberra":
      distanceMethod = CanberraMetric()

    else:
      raise ValueError("distance function not supported by the benchmarks")


    totalTimer = Timer()
    with totalTimer:
		#Choosing a Kernel for the Gaussian Process Classification
      if kernel=="Gaussian":
        kernelMethod = GaussianKernel(width)

      elif kernel=="Polynomial":
        kernelMethod = PolyKernel(cache_size, degree)

      elif kernel=="Sigmoid":
        kernelMethod = SigmoidKernel(cache_size, gamma, coef0)

      elif kernel=="Bessel":
        kernelMethod = BesselKernel(cache_size, order, width,
          degree, distanceMethod)

      elif kernel=="Power":
        kernelMethod = PowerKernel(cache_size, degree, distanceMethod)

      elif kernel=="Log":
        kernelMethod = LogKernel(cache_size, degree, distanceMethod)

      elif kernel=="Cauchy":
        kernelMethod = CauchyKernel(cache_size, sigma, distanceMethod)

      elif kernel=="Constant":
        kernelMethod = ConstKernel(const)

      elif kernel=="Diagonal":
        kernelMethod = DiagKernel(cache_size, const)

      else:
        raise ValueError("kernel not supported by the benchmarks")

      mean_function = ConstMean()
      likelihood = SoftMaxLikelihood()
      inference_method = MultiLaplaceInferenceMethod(kernelMethod,
          self.train_features, mean_function, self.train_labels, likelihood)

      #Create the model
      model = SGPC(inference_method)

      #Train model
      model.train()
      if len(self.data) >= 2:
        predictions = model.apply_multiclass(self.test_features).get_labels()

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
