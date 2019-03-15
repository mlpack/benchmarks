'''
  @file kernel_pca.py
  @author Marcus Edel

  Kernel Principal Components Analysis with scikit.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from sklearn.decomposition import KernelPCA

'''
This class implements the Kernel Principal Components Analysis benchmark.
'''
class SCIKIT_KPCA(object):
  def __init__(self, method_param, run_param):
    self.info = "SCIKIT_KPCA ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])

    self.d = self.data[0].shape[1]
    if "new_dimensionality" in method_param:
      self.d = int(method_param["new_dimensionality"])

    self.kernel = method_param["kernel"]
    if self.kernel == "polynomial" and "degree" in method_param:
      self.degree = int(method_param["degree"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      if self.kernel == "linear":
        model = KernelPCA(n_components=self.d, kernel="linear")
      elif self.kernel == "hyptan":
        model = KernelPCA(n_components=self.d, kernel="sigmoid")
      elif self.kernel == "polynomial":
        model = KernelPCA(n_components=self.d, kernel="poly",
          degree=self.degree)
      elif self.kernel == "cosine":
        model = KernelPCA(n_components=self.d, kernel="cosine",
          degree=self.degree)
      elif self.kernel == "gaussian":
        model = KernelPCA(n_components=self.d, kernel="rbf",
          degree=self.degree)

      out = model.fit_transform(self.data[0])

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
