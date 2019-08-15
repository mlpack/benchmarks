'''
  @file kmeans.py
  @author Marcus Edel

  K-Means Clustering with scikit.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from sklearn.cluster import KMeans

'''
This class implements the K-Means Clustering benchmark.
'''
class SCIKIT_KMEANS(object):
  def __init__(self, method_param, run_param):
    self.info = "SCIKIT_KMEANS ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])

    self.build_opts = {}
    if "clusters" in method_param:
      self.build_opts["n_clusters"] = int(method_param["clusters"])
    if "max_iterations" in method_param:
      self.build_opts["max_iterations"] = int(method_param["max_iterations"])
    if "seed" in method_param:
      self.build_opts["random_state"] = int(method_param["seed"])
      self.build_opts["init"] = "random"
    if "algorithm" in method_param:
      self.build_opts["algorithm"] = str(method_param["algorithm"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      if len(self.data) == 2:
        self.build_opts["init"] = self.data[1]
      kmeans = KMeans(**self.build_opts)
      kmeans.fit(self.data[0])
      labels = kmeans.labels_
      centers = kmeans.cluster_centers_

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
