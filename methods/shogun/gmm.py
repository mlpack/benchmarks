'''
  @file gmm.py
  @author Marcus Edel
  @contributor Rukmangadh Sai Myana

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
This class implements the Gaussian Mixture Model benchmark for Clustering

Notes
-----
The following are the configurable options available for this benchmark:
* gaussians: Number of gaussians to be used by the GMM
* estimation: "EM", "SMEM"

Each estimation method has additional set of options. Check the Shogun
Library's documentation for these. Most of these additional options are
configurable for this benchmark.
'''
class SHOGUN_GMM(object):
  '''
  Create the Gaussina Mixture Model benchmark instance

  @type method_param - dict
  @param method_param - Extra options for the benchmarking method.
  @type run_param - dict
  @param run_param - Path option for executing the benchmark. Not used for
  Shogun.
  '''
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_GMM ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])

    self.g = 3
    if "gaussians" in method_param:
      self.g = int(method_param["gaussians"])

    self.estimation = "EM"
    if "estimation" in method_param:
      self.estimation = str(method_param["estimation"])

    self.max_iter = 1000
    if "max-iterations" in method_param:
      self.max_iter = int(method_param["max-iterations"])

    self.min_cov = 1e-9
    if "min-covariance" in method_param:
      self.min_cov = float(method_param["min-covariance"])

    self.min_change = 1e-9
    if "min-change" in method_param:
      self.min_change = float(method_param["min-change"])

    self.max_cand = 5
    if "max-candidates" in method_param:
      self.max_cand = int(method_param["max-candidates"])

    self.max_em_iter = 1000
    if "max-EM-iterations" in method_param:
      self.max_em_iterations = int(method_param["max-EM-iterations"])

  '''
  Return information about the benchmarking instance

  @rtype - str
  @returns - Information as a single string
  '''
  def __str__(self):
    return self.info

  '''
  Calculate metrics to be used for benchmarking

  @rtype - dict
  @returns - Evaluated metrics
  '''
  def metric(self):
    data_feat = RealFeatures(self.data[0].T)

    totalTimer = Timer()
    with totalTimer:
      model = SGMM(self.g)
      model.set_features(data_feat)
      if self.estimation == "EM":
        model.train_em(self.min_cov, self.max_iter, self.min_change)
      elif self.estimation == "SMEM":
        model.train_smem(self.max_iter, self.max_cand, self.min_cov,
            self.max_em_iter, self.min_change)

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
