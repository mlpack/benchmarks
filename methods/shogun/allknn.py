'''
  @file allknn.py
  @author Marcus Edel

  All K-Nearest-Neighbors with shogun.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from shogun import RealFeatures, MulticlassLabels, EuclideanDistance
from shogun import KNN as SKNN

'''
This class implements the All K-Nearest-Neighbors benchmark.
'''
class SHOGUN_ALLKNN(object):
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_ALLKNN ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.train_feat = RealFeatures(self.data_split[0].T)
    self.train_labels = MulticlassLabels(self.data_split[1])

    if len(self.data) >= 2:
      self.test_feat = RealFeatures(self.data[1].T)

    if "k" in method_param:
      self.k = int(method_param["k"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      distance = EuclideanDistance(self.train_feat, self.train_feat)

      model = SKNN(self.k, distance, self.train_labels)
      model.train()

      if len(self.data) >= 2:
        out = model.apply(self.test_feat).get_labels()
      else:
        out = model.apply(self.train_feat).get_labels()

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
