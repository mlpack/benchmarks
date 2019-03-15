'''
  @file gmm.py
  @author Marcus Edel

  Gaussian Mixture Model with scikit.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from sklearn import mixture

'''
This class implements the Gaussian Mixture Model benchmark.
'''
class SCIKIT_GMM(object):
  def __init__(self, method_param, run_param):
    self.info = "SCIKIT_GMM ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])

    self.build_opts = {}
    if "gaussians" in method_param:
      self.build_opts["n_components"] = int(method_param["gaussians"])
    if "seed" in method_param:
      self.build_opts["random_state"] = int(method_param["seed"])
    if "num_init" in method_param:
      self.build_opts["n_init"] = int(method_param["n_init"])
    if "tolerance" in method_param:
      self.build_opts["tol"] = float(method_param["tolerance"])
    if "max_iterations" in method_param:
      self.build_opts["max_iter"] = int(method_param["max_iterations"])

  def __str__(self):
    return self.info

  def metric(self):
    model = mixture.GaussianMixture(**self.build_opts)

    totalTimer = Timer()
    with totalTimer:
      model.fit(self.data[0])

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
