'''
  @file linear_regression.py
  @author Marcus Edel, Anand Soni

  Linear Regression with scikit.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from sklearn.linear_model import LinearRegression as SLinearRegression

'''
This class implements the Linear Regression benchmark.
'''
class SCIKIT_LINEARREGRESSION(object):
  def __init__(self, method_param, run_param):
    self.info = "SCIKIT_LINEARREGRESSION ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = SLinearRegression()
      model.fit(self.data_split[0], self.data_split[1])

      if len(self.data) >= 2:
        predictions = model.predict(self.data[1])

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    if len(self.data) == 3:
      metric['MSE'] = Metrics.SimpleMeanSquaredError(self.data[2], predictions)

    return metric
