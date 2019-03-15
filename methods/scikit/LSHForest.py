'''
  @file LSHForest.py

  Approximate Nearest Neighbors using LSHForest with scikit.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from sklearn.neighbors import LSHForest

'''
This class implements the Approximate Nearest Neighbors benchmark.
'''
class SCIKIT_ANN(object):
  def __init__(self, method_param, run_param):
    self.info = "SCIKIT_ANN ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])

    self.build_opts = {}
    if "num_trees" in method_param:
      self.build_opts["n_estimators"] = int(method_param["num_trees"])

    if "k" in method_param:
      self.n_neighbors = int(method_param["k"])

    # Lowest hash length to be searched when candidate selection is performed.
    if "min_hash_match" in method_param:
      self.build_opts["min_hash_match"] = int(method_param["min_hash_match"])
    # Minimum number of candidates evaluated per estimator.
    if "num_candidates" in method_param:
      self.build_options["n_candidates"] = int(method_param["n_candidates"])
    # Radius from data point to its neighbors.
    if "radius" in method_param:
      self.build_options["radius"] = float(method_param["radius"])
    # A value ranges from 0 to 1.
    if "radius_cutoff_ratio" in method_param:
      self.build_options["radius_cutoff_ratio"] = float(
        method_param["radius_cutoff_ratio"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = LSHForest(**self.build_opts)
      model.fit(self.data[0])

      distances,indices = model.kneighbors(self.data[1],
        n_neighbors=self.n_neighbors)

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
