'''
  @file allknn.py
  @author Marcus Edel

  All K-Nearest-Neighbors with scikit.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from sklearn.neighbors import NearestNeighbors

'''
This class implements the All K-Nearest-Neighbors benchmark.
'''
class SCIKIT_ALLKNN(object):
  def __init__(self, method_param, run_param):
    self.info = "SCIKIT_ALLKNN ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.build_opts = {}
    if "k" in method_param:
      self.build_opts["n_neighbors"] = int(method_param["k"])
    self.build_opts["leaf_size"] = 20
    if "leaf_size" in method_param:
      self.build_opts["leaf_size"] = int(method_param["leaf_size"])

    if "tree_type" in method_param:
      self.build_opts["tree_type"] = str(method_param["tree_type"])

    if "radius" in method_param:
      self.build_opts["radius"] = float(method_param["radius"])
    if "metric" in method_param:
      self.build_opts["metric"] = str(method_param["metric"])
      if "p" in method_param:
        self.build_opts["p"] = int(method_param["p"])

    if "num_jobs" in method_param:
      self.build_opts["n_jobs"] = int(method_param["num_jobs"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = NearestNeighbors(**self.build_opts)
      model.fit(self.data[0])

      if len(self.data) == 2:
        out = model.kneighbors(self.data[1], self.build_opts["n_neighbors"],
          return_distance=True)
      else:
        # We have to increment k by one because mlpack ignores the
        # self-neighbor, whereas scikit-learn will happily return the
        # nearest neighbor of point 0 as point 0.
        out = model.kneighbors(self.data[0], self.build_opts["n_neighbors"] + 1,
          return_distance=True)

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
