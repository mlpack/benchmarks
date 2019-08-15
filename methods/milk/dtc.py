'''
  @file dtc.py
  @author Marcus Edel

  Decision Tree Classifier with Milk.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *

from milk.supervised import tree_learner

'''
This class implements the Decision Tree Classifier benchmark.
'''
class MILK_DTC(object):
  def __init__(self, method_param, run_param):
    self.info = "MILK_DTC ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.build_opts = {}
    if "minimum_leaf_size" in method_param:
      self.build_opts["min_split"] = int(method_param["minimum_leaf_size"])

  def __str__(self):
    return self.info

  def metric(self):
    model = tree_learner(**self.build_opts)

    totalTimer = Timer()
    with totalTimer:
      model = model.train(self.data_split[0], self.data_split[1])

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()
    return metric
