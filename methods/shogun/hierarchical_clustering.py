'''
  @file hierarchical_clustering.py
  @author Chirag Pabbaraju

  Hierarchical Clustering with shogun.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from shogun import Hierarchical, EuclideanDistance, RealFeatures
from shogun import ManhattanMetric, CosineDistance, ChebyshewMetric

'''
This class implements the Hierarchical Clustering benchmark.
'''
class SHOGUN_HIERARCHICALCLUSTERING(object):
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_HIERARCHICALCLUSTERING ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.method_param = method_param

  def __str__(self):
    return self.info

  def metric(self):
    data_feat = RealFeatures(self.data[0].T)

    # Gather all the parameters.
    if "merges" in self.method_param:
      merges = int(self.method_param["merges"])

    if "distance" in self.method_param:
      distance = str(self.method_param["distance"])
      distance = distance.lower()
      if distance == "euclidean":
        distance = EuclideanDistance(data_feat, data_feat)
      elif distance == "manhattan":
        distance = ManhattanMetric(data_feat, data_feat)
      elif distance == "cosine":
        distance = CosineDistance(data_feat, data_feat)
      elif distance == "chebyshev":
        distance = ChebyshewMetric(data_feat, data_feat)
    else:
      # distance option not specified, default to Euclidean distance
      distance = EuclideanDistance(dataFeat, dataFeat)

    totalTimer = Timer()
    with totalTimer:
      model = Hierarchical(merges, distance)
      model.train()

    merge_distances = model.get_merge_distances()
    cluster_pairs = model.get_cluster_pairs()

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()
    metric["Merge distances between clusters"] = str(merge_distances)
    metric["Cluster pairings"] = str(cluster_pairs)

    return metric
