'''
  @file pca.py
  @author Marcus Edel

  Principal Components Analysis with shogun.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from shogun import RealFeatures
from shogun import PCA as ShogunPCA

'''
This class implements the Principal Components Analysis benchmark.
'''
class SHOGUN_PCA(object):
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_PCA ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])

    self.k = self.data[0].shape[1]
    if "new_dimensionality" in method_param:
      self.k = int(method_param["new_dimensionality"])

    self.s = False
    if "whiten" in method_param:
      self.s = True

    self.data_feat = RealFeatures(self.data[0].T)

  def __str__(self):
    return self.info

  def metric(self):
    data_feat = RealFeatures(self.data[0].T)

    totalTimer = Timer()
    with totalTimer:
      prep = ShogunPCA(self.s)
      prep.set_target_dim(self.k)
      prep.init(self.data_feat)
      prep.apply_to_feature_matrix(self.data_feat)

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
