'''
  @file kmeans.py
  @author Marcus Edel

  K-Means Clustering with shogun.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from shogun import EuclideanDistance, RealFeatures, KMeans, Math_init_random

'''
This class implements the K-Means Clustering benchmark.
'''
class SHOGUN_KMEANS(object):
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_KMEANS ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.method_param = method_param

  def __str__(self):
    return self.info

  def metric(self):
    if "clusters" in self.method_param:
      clusters = int(self.method_param["clusters"])
    maxIterations = None
    if "max_iterations" in self.method_param:
      maxIterations = int(self.method_param["max_iterations"])
    seed = None
    if "seed" in self.method_param:
      seed = int(self.method_param["seed"])

    if seed:
      Math_init_random(seed)

    data_feat = RealFeatures(self.data[0].T)
    distance = EuclideanDistance(data_feat, data_feat)

    totalTimer = Timer()
    with totalTimer:
      if len(self.data) == 2:
        model = KMeans(clusters, distance, self.data[1].T)
      else:
        model = KMeans(clusters, distance)

      if maxIterations:
        model.set_max_iter(maxIterations)
      model.train()

      labels = model.apply().get_labels()
      centers = model.get_cluster_centers()

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
