'''
  @file SVR.py
  @author Saurabh Mahindre

  SVR Regression with scikit.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from sklearn.svm import SVR as SSVR

'''
This class implements the SVR Regression benchmark.
'''
class SCIKIT_SVR(object):
  def __init__(self, method_param, run_param):
    self.info = "SCIKIT_SVR ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.build_opts = {}
    if "c" in method_param:
      self.build_opts["C"] = float(method_param["c"])
    if "epsilon" in method_param:
      self.build_opts["epsilon"] = float(method_param["epsilon"])
    if "gamma" in method_param:
      self.build_opts["gamma"] = float(method_param["gamma"])
    self.build_opts["kernel"] = "rbf"

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = SSVR(**self.build_opts)
      model.fit(self.data_split[0], self.data_split[1])

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
