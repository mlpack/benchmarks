'''
  @file kernel_pca.py
  @author Marcus Edel

  Kernel Principal Components Analysis with shogun.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from shogun import RealFeatures, KernelPCA
from shogun import GaussianKernel, PolyKernel, LinearKernel, SigmoidKernel

'''
This class implements the Kernel Principal Components Analysis benchmark.
'''
class SHOGUN_KPCA(object):
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_KPCA ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.method_param = method_param

  def __str__(self):
    return self.info

  def metric(self):
    data_feat = RealFeatures(self.data[0].T)

    totalTimer = Timer()
    with totalTimer:
      d = self.data[0].shape[1]
      if "new_dimensionality" in self.method_param:
        d = int(self.method_param["new_dimensionality"])

      # Get the kernel type and make sure it is valid.
      if "kernel" in self.method_param:
        kernel = str(self.method_param["kernel"])

      if "degree" in self.method_param:
        degree = int(self.method_param["degree"])

      if kernel == "polynomial":
        kernel = PolyKernel(data_feat, data_feat, degree, True)
      elif kernel == "gaussian":
        kernel = GaussianKernel(data_feat, data_feat, 2.0)
      elif kernel == "linear":
        kernel = LinearKernel(data_feat, data_feat)
      elif kernel == "hyptan":
        kernel = SigmoidKernel(data_feat, data_feat, 2, 1.0, 1.0)

      model = KernelPCA(kernel)
      model.set_target_dim(d)
      model.init(data_feat)
      model.apply_to_feature_matrix(data_feat)

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
