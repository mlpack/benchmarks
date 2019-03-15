'''
  @file gmm.py
  @author Marcus Edel

  Gaussian Mixture Model with shogun.
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
from shogun import GMM as SGMM

'''
This class implements the Gaussian Mixture Model benchmark.
'''
class SHOGUN_GMM(object):
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_GMM ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])

    if "gaussians" in method_param:
      self.g = int(method_param["gaussians"])
    self.n = 0
    if "max_iterations" in method_param:
      self.n = int(method_param["max_iterations"])

  def __str__(self):
    return self.info

  def metric(self):
    data_feat = RealFeatures(self.data[0].T)
    model = SGMM(self.g)
    model.set_features(data_feat)

    totalTimer = Timer()
    with totalTimer:
      model.train_em(1e-9, self.n, 1e-9)

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
