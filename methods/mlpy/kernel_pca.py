'''
  @file kernel_pca.py
  @author Marcus Edel

  Kernel Principal Components Analysis with mlpy.
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
import mlpy

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
  Use the mlpy libary to implement Kernel Principal Components Analysis.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def KPCAMlpy(self, options):
    def RunKPCAMlpy(q):
      totalTimer = Timer()

      # Load input dataset.
      Log.Info("Loading dataset", self.verbose)
      data = np.genfromtxt(self.dataset, delimiter=',')

      try:
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
            d = data.shape[0]

          # Get the kernel type and make sure it is valid.
          if not "kernel" in options:
            Log.Fatal("Choose kernel type, valid choices are 'polynomial', " +
                  "'gaussian', 'linear' and 'hyptan'.")
            q.put(-1)
            return -1

          if options["kernel"] == "polynomial":
            if "degree" in options:
              degree = int(options.pop("degree"))
            else:
              degree = 1

            kernel = mlpy.kernel_polynomial(data, data, d=degree)
          elif options["kernel"] == "gaussian":
            kernel = mlpy.kernel_gaussian(data, data, sigma=2)
          elif options["kernel"] == "linear":
            kernel = mlpy.kernel_linear(data, data)
          elif options["kernel"] == "hyptan":
            kernel = mlpy.kernel_sigmoid(data, data)
          else:
            Log.Fatal("Invalid kernel type (" + kernel.group(1) + "); valid " +
                    "choices are 'polynomial', 'gaussian', 'linear' and 'hyptan'.")
            q.put(-1)
            return -1

          options.pop("kernel")
          if len(options) > 0:
            Log.Fatal("Unknown parameters: " + str(options))
            raise Exception("unknown parameters")

          # Perform Kernel Principal Components Analysis.
          model = mlpy.KPCA()
          model.learn(kernel)
          out = model.transform(kernel, k=d)
      except Exception as e:
        Log.Fatal("Exception: " + str(e))
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunKPCAMlpy, self.timeout)

  '''
  Perform Kernel Principal Components Analysis. If the method has been
  successfully completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform KPCA.", self.verbose)

    results = self.KPCAMlpy(options)
    if results < 0:
      return results

    return {'Runtime' : results}
