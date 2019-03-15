'''
  @file lasso.py
  @author Youssef Emad El-Din

  Lasso Regression with scikit.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from sklearn.linear_model import Lasso

'''
This class implements the Lasso Regression benchmark.
'''
class SCIKIT_LASSO(object):
  def __init__(self, method_param, run_param):
    self.info = "SCIKIT_LASSO ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = Lasso()
      model.fit(self.data[0], self.data[1])
      out = model.coef_

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
