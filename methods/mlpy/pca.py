'''
  @file pca.py
  @author Marcus Edel

  Principal Components Analysis with mlpy.
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
This class implements the Principal Components Analysis benchmark.
'''
class MLPY_PCA(object):
  def __init__(self, method_param, run_param):
    self.info = "MLPY_PCA ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.build_opts = {}
    if "whiten" in method_param:
      self.build_opts["whiten"] = True
    if "new_dimensionality" in method_param:
      self.k = int(method_param["new_dimensionality"])
    else:
      self.k = self.data[0].shape[1]

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = mlpy.PCA(**self.build_opts)
      model.learn(self.data[0])
      out = model.transform(self.data[0], self.k)

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()
    return metric
