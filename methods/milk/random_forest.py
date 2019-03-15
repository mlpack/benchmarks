'''
  @file random_forest.py
  @author Marcus Edel

  Random Forest Classifier with Milk.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from milk.supervised import randomforest
from milk.supervised.multi import one_against_one

'''
This class implements the Random Forest Classifier benchmark.
'''
class MILK_RANDOMFOREST(object):
  def __init__(self, method_param, run_param):
    self.info = "MILK_RANDOMFOREST ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.build_opts = {}
    if "num_trees" in method_param:
      self.build_opts["rf"] = int(method_param["num_trees"])

  def __str__(self):
    return self.info

  def metric(self):
    weak_learner = randomforest.rf_learner(**self.build_opts)
    model = one_against_one(weak_learner)

    totalTimer = Timer()
    with totalTimer:
      model = model.train(self.data_split[0], self.data_split[1])

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()
    return metric
