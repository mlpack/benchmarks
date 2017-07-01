'''
  @file pca.py
  @author Marcus Edel

  Principal Components Analysis with scikit.
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
from sklearn import decomposition

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
  Use the scikit libary to implement Principal Components Analysis.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def PCAScikit(self, options):
    def RunPCAScikit(q):
      totalTimer = Timer()

      # Load input dataset.
      Log.Info("Loading dataset", self.verbose)
      data = np.genfromtxt(self.dataset, delimiter=',')

      try:
        with totalTimer:
          # Find out what dimension we want.
          opts={}
          if "new_dimensionality" in options:
            opts["n_components"] = int(options.pop("new_dimensionality"))
            if (opts["n_components"] > data.shape[1]):
              Log.Fatal("New dimensionality (" + str(k) + ") cannot be greater "
                  + "than existing dimensionality (" + str(data.shape[1]) + ")!")
              q.put(-1)
              return -1
          else:
            opts["n_components"] = data.shape[1]
          if "whiten" in options:
            opts["whiten"] = True
            options.pop("whiten")

          if len(options) > 0:
            Log.Fatal("Unknown parameters: " + str(options))
            raise Exception("unknown parameters")

          # Perform PCA.
          pca = decomposition.PCA(**opts)
          pca.fit(data)
          score = pca.transform(data)
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunPCAScikit, self.timeout)

  '''
  Perform Principal Components Analysis. If the method has been successfully
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform PCA.", self.verbose)

    results = self.PCAScikit(options)
    if results < 0:
      return results

    return {'Runtime' : results}
