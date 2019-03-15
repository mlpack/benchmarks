'''
  @file kernel_pca.py
  @author Marcus Edel

  Kernel Principal Components Analysis with mlpy.
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
This class implements the Kernel Principal Components Analysis benchmark.
'''
class MLPY_KPCA(object):
  def __init__(self, method_param, run_param):
    self.info = "MLPY_KPCA ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    if len(self.data) == 1:
      self.data = split_dataset(self.data[0])

    self.build_opts = {}
    self.build_opts["k"] = self.data[0].shape[1]
    if "new_dimensionality" in method_param:
      self.build_opts["k"] = int(method_param["new_dimensionality"])

    self.method_param = method_param

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      if self.method_param["kernel"] == "polynomial":
        if "degree" in self.method_param:
          degree = int(self.method_param["degree"])
        else:
          degree = 1

        kernel = mlpy.kernel_polynomial(self.data[0], self.data[0], d=degree)
      elif self.method_param["kernel"] == "gaussian":
        kernel = mlpy.kernel_gaussian(self.data[0], self.data[0], sigma=2)
      elif self.method_param["kernel"] == "linear":
        kernel = mlpy.kernel_linear(self.data[0], self.data[0])
      elif self.method_param["kernel"] == "hyptan":
        kernel = mlpy.kernel_sigmoid(self.data[0], self.data[0])

      model = mlpy.KPCA()
      model.learn(kernel)
      out = model.transform(kernel, **self.build_opts)

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()
    return metric
