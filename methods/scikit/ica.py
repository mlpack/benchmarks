'''
  @file ica.py
  @author Marcus Edel

  Independent component analysis with scikit.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from sklearn.decomposition import FastICA

'''
This class implements the independent component analysis benchmark.
'''
class SCIKIT_ICA(object):
  def __init__(self, method_param, run_param):
    self.info = "SCIKIT_ICA ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])

    self.build_opts = {}
    if "num_components" in method_param:
      self.build_opts["n_components"] = int(method_param["num_components"])

    if "algorithm" in method_param:
      self.build_opts["algorithm"] = str(method_param["algorithm"])

    if "function" in method_param:
      self.build_opts["fun"] = str(method_param["function"])

    if "tolerance" in method_param:
      self.build_opts["tol"] = float(method_param["tolerance"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = FastICA(**self.build_opts)
      ic = model.fit(self.data[0]).transform(self.data[0])

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
