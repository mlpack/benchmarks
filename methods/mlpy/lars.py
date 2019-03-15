'''
  @file lars.py
  @author Marcus Edel

  Least Angle Regression with mlpy.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
import mlpy

'''
This class implements the Least Angle Regression benchmark.
'''
class MLPY_LARS(object):
  def __init__(self, method_param, run_param):
    self.info = "MLPY_LARS ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    if len(self.data) == 1:
      self.data = split_dataset(self.data[0])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = mlpy.LARS()
      model.learn(self.data[0], self.data[1])
      output = model.beta()

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()
    return metric
