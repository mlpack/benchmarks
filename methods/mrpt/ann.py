'''
  @file ann.py
  @author Marcus Edel

  Class to benchmark the MRPT Approximate Nearest Neighbors method.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
import mrpt

'''
This class implements the Approximate K-Nearest-Neighbors benchmark.
'''
class MRPT_ANN(object):
  def __init__(self, method_param, run_param):
    self.info = "MRPT_ANN ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    if len(self.data) == 1:
      self.data = split_dataset(self.data[0])

    self.build_dict = {}
    self.build_dict["depth"] = 2
    self.run_dict = {}
    self.run_dict["votes_required"] = 1
    if "num_trees" in method_param:
      self.build_dict["n_trees"] = int(method_param["num_trees"])
    if "depth" in method_param:
      self.build_dict["depth"] = int(method_param["depth"])
    if "votes_required" in method_param:
      self.run_dict["votes_required"] = int(method_param["votes_required"])
    if "k" in method_param:
      self.k = int(method_param["k"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      index = mrpt.MRPTIndex(np.float32(self.data[0]))
      index.build(**self.build_dict)
      neighbors = np.zeros((len(self.data[1]), self.k))
      for i in range(len(self.data[1])):
          neighbors[i] = index.ann(np.float32(self.data[1][i]), self.k,
          **self.run_dict)

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()
    return metric
