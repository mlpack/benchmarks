'''
  @file ann.py

  Class to benchmark the Annoy Approximate Nearest Neighbors method.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from annoy import AnnoyIndex

'''
This class implements the Approximate K-Nearest-Neighbors benchmark.
'''
class ANNOY_ANN(object):
  def __init__(self, method_param, run_param):
    self.info = "ANNOY_ANN ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.build_opts = {}
    if "k" in method_param:
      self.build_opts["k"] = int(method_param["k"])
    if "num_trees" in method_param:
      self.build_opts["num_trees"] = int(method_param["num_trees"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      t = AnnoyIndex(self.data_split[0].shape[1])
      for i in range(len(self.data_split[0])):
          t.add_item(i, self.data_split[0][i])
      t.build(self.build_opts["num_trees"])
      for i in range(len(self.data[1])):
          v = t.get_nns_by_vector(self.data[1][i], self.build_opts["k"])

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()
    return metric
