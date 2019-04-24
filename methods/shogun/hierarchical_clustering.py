'''
  @file hierarchical_clustering.py
  @author Chirag Pabbaraju
  @contributor Rukmangadh Sai Myana

  Hierarchical Clustering with shogun.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from shogun import Hierarchical, RealFeatures
from shogun import (
  EuclideanDistance,
  ChiSquareDistance,
  CosineDistance,
  TanimotoDistance,
  MinkowskiMetric,
  ManhattanMetric,
  JensenMetric,
  CanberraMetric,
  ChebyshewMetric,
  GeodesicMetric
  )

'''
This class implements the Hierarchical Clustering benchmark for Clustering.

Notes
-----
The following are the configurable options available for this benchmark:
* merges: Number of merges to take place
* distance: "Euclidean", "Chi-Square", "Cosine", "Tanimoto", "Minkowski",
"Manhattan", "Jensen", "Canberra", "Chebyshev", "Geodesic"
'''
class SHOGUN_HIERARCHICALCLUSTERING(object):
  '''
  Create the Hierarchical Clustering benchmarking instance.

  @type method_param - dict
  @param method_param - Extra options for the benchmarking method.
  @type run_param - dict
  @param run_param - Path option for executing the benchmark. Not used for
  Shougn.
  '''
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_HIERARCHICALCLUSTERING ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])

    self.merges = 4
    if "merges" in method_param:
      self.merges = int(method_param["merges"])

    self.distance = "Euclidean"
    if "distance" in method_param:
      self.distance = str(method_param["distance"])

    self.minkowski_k = 3
    if "k" in method_param:
      self.minkowski_k = float(method_param["k"])

  '''
  Return information about the benchmarking instance.

  @rtype - str
  @returns - Information as a single string.
  '''
  def __str__(self):
    return self.info

  '''
  Calculate metrics to be used for benchmarking

  @rtype - dict
  @returns - Evaluated metrics
  '''
  def metric(self):
    totalTimer = Timer()

    with totalTimer:
      data_feat = RealFeatures(self.data[0].T)

      if self.distance == "Euclidean":
        distanceMethod = EuclideanDistance(data_feat, data_feat)

      elif self.distance == "Manhattan":
        distanceMethod = ManhattanMetric(data_feat, data_feat)

      elif self.distance == "Cosine":
        distanceMethod = CosineDistance(data_feat, data_feat)

      elif self.distance == "Chebyshev":
        distanceMethod = ChebyshewMetric(data_feat, data_feat)

      elif self.distance == "Chi-Square":
        distanceMethod = ChiSquareDistance(data_feat, data_feat)

      elif self.distance == "Tanimoto":
        distanceMethod = TanimotoDistance(data_feat, data_feat)

      elif self.distance == "Minkowski":
        distanceMethod = MinkowskiMetric(data_feat, data_feat, self.minkowski_k)

      elif self.distance == "Jensen":
        distanceMethod = JensenMetric(data_feat, data_feat)

      elif self.distance == "Canberra":
        distanceMethod = CanberraMetric(data_feat, data_feat)

      elif self.distance == "Geodesic":
        distanceMethod = GeodesicMetric(data_feat, data_feat)

      else:
        raise ValueError("Provided distance not supported by the benchmark")

      model = Hierarchical(self.merges, distanceMethod)
      model.train()

    merge_distances = model.get_merge_distances()
    cluster_pairs = model.get_cluster_pairs()

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()
    metric["Merge distances between clusters"] = str(merge_distances)
    metric["Cluster pairings"] = str(cluster_pairs)

    return metric
