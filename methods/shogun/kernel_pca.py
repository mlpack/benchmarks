'''
  @file kernel_pca.py
  @author Marcus Edel

  Kernel Principal Components Analysis with shogun.
'''

import os
import sys
import inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from log import *
from timer import *

import numpy as np
from modshogun import RealFeatures, KernelPCA
from modshogun import GaussianKernel, PolyKernel, LinearKernel, SigmoidKernel

'''
This class implements the Kernel Principal Components Analysis benchmark.
'''
class KPCA(object):

  '''
  Create the Kernel Principal Components Analysis benchmark instance.

  @param dataset - Input dataset to perform KPCA on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout

  '''
  Use the shogun libary to implement Kernel Principal Components Analysis.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def KPCAShogun(self, options):
    def RunKPCAShogun(q):
      totalTimer = Timer()

      try:
        # Load input dataset.
        Log.Info("Loading dataset", self.verbose)
        data = np.genfromtxt(self.dataset, delimiter=',')
        dataFeat = RealFeatures(data.T)

        with totalTimer:
          # Get the new dimensionality, if it is necessary.
          if "new_dimensionality" in options:
            d = int(options.pop("new_dimensionality"))
            if (d > data.shape[1]):
              Log.Fatal("New dimensionality (" + str(d) + ") cannot be greater "
                + "than existing dimensionality (" + str(data.shape[1]) + ")!")
              q.put(-1)
              return -1
          else:
            d = data.shape[1]

          # Get the kernel type and make sure it is valid.
          if "kernel" in options:
            kernel = str(options.pop("kernel"))
          else:
            Log.Fatal("Choose kernel type, valid choices are 'linear'," +
                  " 'hyptan', 'polynomial' and 'gaussian'.")
            q.put(-1)
            return -1

          if "degree" in options:
            degree = int(options.pop("degree"))

          if len(options) > 0:
            Log.Fatal("Unknown parameters: " + str(options))
            raise Exception("unknown parameters")

          if kernel == "polynomial":
            kernel = PolyKernel(dataFeat, dataFeat, degree, True)
          elif kernel == "gaussian":
            kernel = GaussianKernel(dataFeat, dataFeat, 2.0)
          elif kernel == "linear":
            kernel = LinearKernel(dataFeat, dataFeat)
          elif kernel == "hyptan":
            kernel = SigmoidKernel(dataFeat, dataFeat, 2, 1.0, 1.0)
          else:
            Log.Fatal("Invalid kernel type (" + kernel.group(1) + "); valid "
              + "choices are 'linear', 'hyptan', 'polynomial' and 'gaussian'.")
            q.put(-1)
            return -1

          # Perform Kernel Principal Components Analysis.
          model = KernelPCA(kernel)
          model.set_target_dim(d)
          model.init(dataFeat)
          model.apply_to_feature_matrix(dataFeat)
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunKPCAShogun, self.timeout)

  '''
  Perform Kernel Principal Components Analysis. If the method has been
  successfully completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform KPCA.", self.verbose)

    results = self.KPCAShogun(options)
    if results < 0:
      return results

    return {'Runtime' : results}
