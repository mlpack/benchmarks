'''
  @file pca.py
  @author Marcus Edel
  @contributor Rukmangadh Sai Myana

  Principal Components Analysis with shogun.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from shogun import RealFeatures
from shogun import PCA
from shogun import (
  FIXED_NUMBER,
  VARIANCE_EXPLAINED,
  THRESHOLD
  )
from shogun import (
  AUTO,
  SVD,
  EVD
  )
from shogun import (
  MEM_REALLOCATE,
  MEM_IN_PLACE
  )

'''
This class implements the Principal Components Analysis benchmark.

Notes
-----
The following are the configurable options available for this benchmark:

* pca-mode: "fixed"(The target dimensions are given provided), "variance"(The
target dimensions are inferred from the threshold provided), "threshold"(The
target dimensions are inferred from the threshold provided)

* decomposition: "svd"(SVD decomposition is used for PCA), "evd"(EVD is used
for PCA), "auto"(autoselect the decompostion method to be used)

* memory-mode: "reallocate"(Reallocate memory for the new matrix),
"in-place"(No new reallocation. Memory of the old matrix is used.)

* target-dimensions: The new dimensions/dimensionality of the new matrix when
the "fixed" pca-mode is used.

* threshold: The threshold value used when the "variance" and "threshold"
pca-modes are used.

* whiten: Whether to normalized the columns of the PCA transformation matrix

Check Shogun's Official documentation for more information.
'''
class SHOGUN_PCA(object):

  '''
  Create the Principal Components Analysis benchmark instance.
  
  @type method_param - dict
  @param method_param - Extra options for the benchmarking method.
  @type run_param - dict
  @param run_param - Path option for executing the benckmark. Not used for 
  Shogun.
  '''
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_PCA ("  + str(method_param) +  ")"

    # Assemble run model parameters.
    self.data = load_dataset(method_param["datasets"], ["csv"])

    self.pca_mode = "fixed"
    if "pca-mode" in method_param:
      self.pca_mode = str(method_param["pca-mode"])

    self.decomposition_method = "auto"
    if "decomposition" in method_param:
      self.decomposition_method = str(method_param["decomposition"])

    self.memory_mode = "reallocate"
    if "memory-mode" in method_param:
      self.memory_mode = str(method_param["memory-mode"])

    self.target_dim = self.data[0].shape[1]
    if "target-dimensions" in method_param:
      self.target_dim = int(method_param["target-dimensions"])

    self.threshold = 1e-6
    if "threshold" in method_param:
      self.threshold = float(method_param["threshold"])

    self.do_whitening = False
    if "whiten" in method_param:
      self.do_whitening = bool(method_param["whiten"])

    self.data_feat = RealFeatures(self.data[0].T)

  '''
  Return information about the benchmarking instance.

  @rtype - str
  @returns - Information as a single string.
  '''
  def __str__(self):
    return self.info

  '''
  Calculate metrics to be used for benchmarking.

  @rtype - dict
  @returns - Evaluated metrics.
  '''
  def metric(self):

    totalTimer = Timer()

    with totalTimer:
      data_feat = RealFeatures(self.data[0].T)

      if self.memory_mode == "reallocate":
        MemoryMode = MEM_REALLOCATE

      elif self.memory_mode == "in-place":
        MemoryMode = MEM_IN_PLACE

      else:
        raise ValueError("Provide memory-mode not supported by benchmark")

      if self.decomposition_method == "auto":
        PCAMethod = AUTO

      elif self.decomposition_method == "svd":
        PCAMethod = SVD

      elif self.decomposition_method == "evd":
        PCAMethod = EVD

      else:
        raise ValueError("Provided decomposition strategy not supported")

      if self.pca_mode == "fixed":
        prep = PCA(PCAMethod, self.do_whitening, MemoryMode)
        prep.set_target_dim(self.target_dim)

      elif self.pca_mode == "variance":
        prep = PCA(self.do_whitening, VARIANCE_EXPLAINED, self.threshold,
          PCAMethod, MemoryMode)

      elif self.pca_mode == "threshold":
        prep = PCA(self.do_whitening, THRESHOLD, self.threshold, PCAMethod, 
          MemoryMode)

      else:
        raise ValueError("Provided pca-mode not supported by current benchmark")

      prep.init(self.data_feat)
      prep.apply_to_feature_matrix(self.data_feat)

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
