'''
  @file elastic_net.py
  @author Marcus Edel

  Elastic Net Classifier with scikit.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from sklearn.linear_model import ElasticNet as SElasticNet

'''
This class implements the Elastic Net Classifier benchmark.
'''
class SCIKIT_ELASTICNET(object):
  def __init__(self, method_param, run_param):
    self.info = "SCIKIT_ELASTICNET ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.build_opts = {}
    if "rho" in method_param:
      self.build_opts["rho"] = float(method_param["rho"])
    if "alpha" in method_param:
      self.build_opts["alpha"] = float(method_param["alpha"])
    if "max_iterations" in method_param:
      self.build_opts["max_iter"] = int(method_param["max_iterations"])
    if "tolerance" in method_param:
      self.build_opts["tol"] = float(method_param["tolerance"])
    if "selection" in method_param:
      self.build_opts["selection"] = str(method_param["selection"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = SElasticNet(**self.build_opts)
      model.fit(self.data_split[0], self.data_split[1])
      predictions = model.predict(self.data[1])

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    if len(self.data) == 3:
      metric['MSE'] = Metrics.SimpleMeanSquaredError(self.data[2], predictions)

    return metric
