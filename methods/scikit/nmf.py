'''
  @file nmf.py
  @author Marcus Edel

  Non-negative Matrix Factorization with scikit.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from sklearn.decomposition import NMF as ScikitNMF

'''
This class implements the Non-negative Matrix Factorization benchmark.
'''
class SCIKIT_NMF(object):
  def __init__(self, method_param, run_param):
    self.info = "SCIKIT_NMF ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])

    self.build_opts = {}
    if "rank" in method_param:
      self.build_opts["n_components"] = int(method_param["rank"])
    if "max_iterations" in method_param:
      self.build_opts["max_iter"] = int(method_param["max_iterations"])
    if "tolerance" in method_param:
      self.build_opts["tol"] = float(method_param["tolerance"])
    self.build_opts["init"] = "nndsvdar"
    if "seed" in method_param:
      self.build_opts["init"] = "random"
      self.build_opts["random_state"] = int(method_param["seed"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = ScikitNMF(**self.build_opts)
      W = model.fit_transform(self.data[0])
      H = model.components_

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
