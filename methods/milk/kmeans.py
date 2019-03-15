'''
  @file kmeans.py
  @author Marcus Edel

  K-Means Clustering with milk.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from milk import kmeans

'''
This class implements the K-Means Clustering benchmark.
'''
class MILK_KMEANS(object):
  def __init__(self, method_param, run_param):
    self.info = "MLPY_KMEANS ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])

    self.build_opts = {}
    self.build_opts["return_centroids"] = True
    self.clusters = 0
    if "clusters" in method_param:
      self.clusters = int(method_param["clusters"])
    self.build_opts["max_iterations"] = 1000
    if "max_iterations" in method_param:
      self.build_opts["max_iterations"] = int(method_param["max_iterations"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      if len(self.data) == 1:
        assignments = kmeans(self.data[0], self.clusters, **self.build_opts)
      else:
        self.build_opts["centroids"] = self.data[1]
        assignments = kmeans(self.data[0], self.clusters, **self.build_opts)

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()
    return metric
