'''
  @file kmeans.py
  @author Marcus Edel
  @contributor Rukmangadh Sai Myana

  Llyod K-Means Clustering with shogun.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from shogun import RealFeatures, KMeans, Math_init_random
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
This class implements the K-Means Clustering benchmark.

Notes
-----
The following configurable options are supported by this benchmark:
* distance: "Euclidean", "Bray-Curtis", "Chi-Square", "Mahalanobis", "Cosine",
"Tanimoto", "Minkowski", "Manhattan", "Jensen", "Chebyshev", "Canberra",
"Geodesic"

* cluster: The number of clusters after clustering.

* max-iterations: The maximum number of iterations in the Llyod KMeans algo.

* seed: Seed to be used in the random value generator when initializing the
cluster centers by random.

* use-kmeanspp: True (Use KMeans Plus Plus for initializing centers), False (
Use random initialization)

Other additional options may be needed by some of the distance functions. Most
of such options are configurable in the this benchmark. See Shogun Library's
Documentation for these extra options.
'''
class SHOGUN_KMEANS(object):
  '''
  Create the K-Means benchmark instance.
  
  @type method_param - dict
  @param method_param - Extra options for the benchmarking method.
  @type run_param - dict
  @param run_param - Path option for executing the benchmark. Not used for
  Shogun.
  '''
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_KMEANS ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])

    self.k = 4
    if "clusters" in method_param:
      self.k = int(method_param["clusters"])

    self.distance = "Euclidean"
    if "distance" in method_param:
      self.distance = str(method_param["distance"])

    self.max_iter = None
    if "max-iterations" in method_param:
      self.max_iter = int(method_param["max-iterations"])

    self.seed = None
    if "seed" in method_param:
      self.seed = int(method_param["seed"])

    self.use_kmpp = False
    if "use-kmeanspp" in method_param:
      self.use_kmpp = bool(method_param["use-kmeanspp"])

    self.minkowski_k = 3
    if "minkowski_k" in method_param:
      self.minkowski_k = float(method_param["minkowski_k"])

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
      if self.seed:
        Math_init_random(self.seed)

      data_feat = RealFeatures(self.data[0].T)
      if self.distance == "Euclidean":
        distanceMethod = EuclideanDistance(data_feat, data_feat)

      elif self.distance == "Bray-Curtis":
        distanceMethod = BrayCurtisDistance(data_feat, data_feat)

      elif self.distance == "Chi-Square":
        distanceMethod = ChiSquareDistance(data_feat, data_feat)

      elif self.distance == "Mahalanobis":
        distanceMethod = MahalanobisDistance(data_feat, data_feat)

      elif self.distance == "Cosine":
        distanceMethod = CosineDistance(data_feat, data_feat)

      elif self.distance == "Tanimoto":
        distanceMethod = TanimotoDistance(data_feat, data_feat)

      elif self.distance == "Minkowski":
        distanceMethod = MinkowskiMetric(data_feat, data_feat, self.minkowski_k)

      elif self.distance == "Manhattan":
        distanceMethod = ManhattanMetric(data_feat, data_feat)

      elif self.distance == "Jensen":
        distanceMethod = JensenMetric(data_feat, data_feat)

      elif self.distance == "Chebyshev":
        distanceMethod = ChebyshewMetric(data_feat, data_feat)

      elif self.distance == "Canberra":
        distanceMethod = CanberraMetric(data_feat, data_feat)

      elif self.distance == "Geodesic":
        distanceMethod = GeodesicMetric(data_feat, data_feat)

      else:
        raise ValueError("Provided distance not supported by benchmark")

      model = KMeans(self.k, distanceMethod, self.use_kmpp)

      if self.max_iter:
        model.set_max_iter(self.max_iter)
      model.train()

      labels = model.apply().get_labels()
      centers = model.get_cluster_centers()

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
