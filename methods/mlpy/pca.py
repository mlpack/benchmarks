'''
  @file pca.py
  @author Marcus Edel

  Principal Components Analysis with mlpy.
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
This class implements the Principal Components Analysis benchmark.
'''
class PCA(object):

  '''
  Create the Principal Components Analysis benchmark instance.

  @param dataset - Input dataset to perform PCA on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout

  '''
  Use the mlpy libary to implement Principal Components Analysis.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def PCAMlpy(self, options):
    def RunPCAMlpy(q):
      totalTimer = Timer()

      # Load input dataset.
      Log.Info("Loading dataset", self.verbose)
      data = np.genfromtxt(self.dataset, delimiter=',')

      try:
        with totalTimer:
          # Find out what dimension we want.
          if "new_dimensionality" in options:
            k = int(options.pop("new_dimensionality"))
            if (k > data.shape[1]):
              Log.Fatal("New dimensionality (" + str(k) + ") cannot be greater "
                  + "than existing dimensionality (" + str(data.shape[1]) + ")!")
              q.put(-1)
              return -1
          else:
            k = data.shape[1]

          build_opts = {}
          if "whiten" in options:
            build_opts["whiten"] = True
            options.pop("whiten")

          if len(options) > 0:
            Log.Fatal("Unknown parameters: " + str(options))
            raise Exception("unknown parameters")

          # Perform PCA.
          prep = mlpy.PCA(**build_opts)
          prep.learn(data)
          out = prep.transform(data, k)
      except Exception as e:
        Log.Fatal("Exception: " + str(e))
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunPCAMlpy, self.timeout)

  '''
  Perform Principal Components Analysis. If the method has been successfully
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform PCA.", self.verbose)

    results = self.PCAMlpy(options)
    if results < 0:
      return results

    return {'Runtime' : results}
