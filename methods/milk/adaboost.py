'''
  @file adaboost.py
  AdaBoost classifier with Milk.
'''
import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *

import milk.supervised.tree
import milk.supervised.adaboost
from milk.supervised.multi import one_against_one

'''
This class implements the AdaBoost classifier benchmark.
'''
class MILK_ADABOOST(object):
  def __init__(self, method_param, run_param):
    self.info = "MILK_ADABOOST ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

  def __str__(self):
    return self.info

  def metric(self):
    weak = milk.supervised.tree.stump_learner()
    model = milk.supervised.adaboost.boost_learner(weak)
    model = one_against_one(model)

    totalTimer = Timer()
    with totalTimer:
      model = model.train(self.data_split[0], self.data_split[1])

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()
    return metric
