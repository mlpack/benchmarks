'''
  @file nmf.py
  @author Marcus Edel

  Non-negative Matrix Factorization with scikit.
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
from sklearn.decomposition import NMF as ScikitNMF

'''
This class implements the Non-negative Matrix Factorization benchmark.
'''
class NMF(object):

  '''
  Create the Non-negative Matrix Factorization benchmark instance.

  @param dataset - Input dataset to perform NMF on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout

  '''
  Use the scikit libary to implement Non-negative Matrix Factorization.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def NMFScikit(self, options):
    def RunNMFScikit(q):
      totalTimer = Timer()

      # Load input dataset.
      Log.Info("Loading dataset", self.verbose)
      data = np.genfromtxt(self.dataset, delimiter=',')

      try:
        with totalTimer:
          # Gather parameters.
          opts = {}
          if "rank" in options:
            opts["n_components"] = int(options.pop("rank"))
          else:
            Log.Fatal("Required parameter 'rank' not specified!")
            raise Exception("missing parameter")
          if "max_iterations" in options:
            opts["max_iter"] = int(options.pop("max_iterations"))
          if "tolerance" in options:
            opts["tol"] = float(options.pop("tolerance"))
          if "seed" in options:
            opts["init"] = "random"
            opts["random_state"] = int(options.pop("seed"))
          else:
            opts["init"] = "nndsvdar"

          if len(options) > 0:
            Log.Fatal("Unknown parameters: " + str(options))
            raise Exception("unknown parameters")

          # Perform NMF with the specified update rules.
          model = ScikitNMF(**opts)

          W = model.fit_transform(data)
          H = model.components_
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunNMFScikit, self.timeout)

  '''
  Perform Non-negative Matrix Factorization. If the method has been successfully
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform NMF.", self.verbose)

    results = self.NMFScikit(options)
    if results < 0:
      return results

    return {'Runtime' : results}
