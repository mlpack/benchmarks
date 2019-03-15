'''
  @file pca.py
  @author Marcus Edel

  Principal Components Analysis with scikit.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from sklearn import decomposition

'''
This class implements the Principal Components Analysis benchmark.
'''
class SCIKIT_PCA(object):
  def __init__(self, method_param, run_param):
    self.info = "SCIKIT_PCA ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])

    self.build_opts = {}
    if "new_dimensionality" in method_param:
      self.build_opts["n_components"] = int(method_param["new_dimensionality"])
    else:
      self.build_opts["n_components"] = self.data[0].shape[1]
    if "whiten" in method_param:
      self.build_opts["whiten"] = True

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = decomposition.PCA(**self.build_opts)
      model.fit(self.data[0])
      score = model.transform(self.data[0])

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    return metric
