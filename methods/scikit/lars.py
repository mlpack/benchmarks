'''
  @file lars.py
  @author Marcus Edel

  Least Angle Regression with scikit.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from sklearn.linear_model import LassoLars

'''
This class implements the Least Angle Regression benchmark.
'''
class SCIKIT_LARS(object):
  def __init__(self, method_param, run_param):
    self.info = "SCIKIT_LARS ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])

    self.build_opts = {}
    if "lambda1" in method_param:
      self.build_opts["alpha"] = float(method_param["lambda1"])
    if "max_iterations" in method_param:
      self.build_opts["max_iter"] = int(method_param["max_iterations"])
    if "epsilon" in method_param:
      self.build_opts["eps"] = float(method_param["epsilon"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = LassoLars(**self.build_opts)
      model.fit(self.data[0], self.data[1])
      out = model.coef_

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
