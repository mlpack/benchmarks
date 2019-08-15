'''
  @file knn.py
  @author Marcus Edel
  @contributor Rukmangadh Sai Myana

  K-Nearest-Neighbors Classification with shogun.
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
from shogun import KNN as SKNN
from shogun import KNN_BRUTE, KNN_KDTREE, KNN_COVER_TREE, KNN_LSH

'''
This class implements the K-Nearest-Neighbors benchmark for Multi-class 
classification.

Notes
-----
The following are the configurable options available for this benchmark:
* distance: "Euclidean", "Bray-Curtis", "Chi-Square", "Mahalanobis", "Cosine",
"Tanimoto", "Minkowski", "Manhattan", "Jensen", "Chebyshev", "Canberra",
"Geodesic"
* solver: "Brute", "KD-Tree", "Cover-Tree", "LSH"

Some distance functions might need additional options for using them. These 
options can be found in Shogun Library's official documentation. Most of these 
additional options are configurable.
'''
class SHOGUN_KNN(object):
  '''
  Create the K-Nearest Neighbours benchmark instance.

  @type method_param - dict
  @param method_param - Extra options for the benchmarking method.
  @type run_param - dict
  @param run_param - Path option for executing the benchmark. Not used for
  Shogun.
  '''
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_KNN ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.train_feat = RealFeatures(self.data_split[0].T)

	# Encode the labels into {0,1,2,3,......,num_classes-1}
    self.train_labels, self.label_map = label_encoder(self.data_split[1])
    self.train_labels = MulticlassLabels(self.train_labels)


    if len(self.data) >= 2:
      self.test_feat = RealFeatures(self.data[1].T)

    self.k = 3
    if "k" in method_param:
      self.k = int(method_param["k"])

    self.distance = "Euclidean"
    if "distance" in method_param:
      self.distance = str(method_param["distance"])

    self.solver = "Brute"
    if "solver" in method_param:
      self.solver = str(method_param["solver"])

    self.degree = 3
    if "degree" in method_param:
      self.degree = float(method_param["degree"])

  '''
  Return Information about the benchmarking instance.

  @rtype - str
  @returns - Information as a single string.
  '''
  def __str__(self):
    return self.info

  '''
  Calculate the metrics to be used for benchmarking.

  @rtype - dict
  @returns - Evaluated metrics
  '''
  def metric(self):
    totalTimer = Timer()

    with totalTimer:
      if self.distance=="Euclidean":
        distanceMethod = EuclideanDistance(self.train_feat, self.train_feat)

      elif self.distance=="Bray-Curtis":
        distanceMethod = BrayCurtisDistance(self.train_feat, self.train_feat)

      elif self.distance=="Chi-Square":
        distanceMethod = ChiSquareDistance(self.train_feat, self.train_feat)

      elif self.distance=="Mahalanobis":
        distanceMethod = MahalanobisDistance(self.train_feat, self.train_feat)

      elif self.distance=="Cosine":
        distanceMethod = CosineDistance(self.train_feat, self.train_feat)

      elif self.distance=="Tanimoto":
        distanceMethod = TanimotoDistance(self.train_feat, self.train_feat)

      elif self.distance=="Minkowski":
        distanceMethod = MinkowskiMetric(self.train_feat, self.train_feat,
            self.degree)

      elif self.distance=="Manhattan":
        distanceMethod = ManhattanMetric(self.train_feat, self.train_feat)

      elif self.distance=="Jensen":
        distanceMethod = JensenMetric(self.train_feat, self.train_feat)

      elif self.distance=="Chebyshev":
        distanceMethod = ChebyshewMetric(self.train_feat, self.train_feat)

      elif self.distance=="Canberra":
        distanceMethod = CanberraMetric(self.train_feat, self.train_feat)

      elif self.distance=="Geodesic":
        distanceMethod = GeodesicMetric(self.train_feat, self.train_feat)

      else:
        raise ValueError("Provided distance not supported by benchmark")

      if self.solver == "Brute":
        solverFlag = KNN_BRUTE

      elif self.solver == "KD-Tree":
        solverFlag = KNN_KDTREE

      elif self.solver == "Cover-Tree":
        solverFlag = KNN_COVER_TREE

      elif self.solver == "LSH":
        solverFlag = KNN_LSH

      else:
        raise ValueError("Provided solver not supported by benchmark")

      model = SKNN(self.k, distanceMethod, self.train_labels, solverFlag)
      model.train()

      if len(self.data) >= 2:
        predictions = model.apply_multiclass(self.test_feat).get_labels()

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
