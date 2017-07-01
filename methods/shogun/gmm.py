'''
  @file gmm.py
  @author Marcus Edel

  Gaussian Mixture Model with shogun.
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
from modshogun import RealFeatures
from modshogun import GMM as SGMM

'''
This class implements the Gaussian Mixture Model benchmark.
'''
class GMM(object):

  '''
  Create the Gaussian Mixture Model benchmark instance.

  @param dataset - Input dataset to perform Gaussian Mixture Model on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout

  '''
  Use the shogun libary to implement Gaussian Mixture Model.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def GMMShogun(self, options):
    def RunGMMShogun(q):
      totalTimer = Timer()

      try:
        # Load input dataset.
        Log.Info("Loading dataset", self.verbose)
        dataPoints = np.genfromtxt(self.dataset, delimiter=',')
        dataFeat = RealFeatures(dataPoints.T)

        # Get all the parameters.
        if "gaussians" in options:
          g = int(options.pop("gaussians"))
        else:
          Log.Fatal("Required parameter 'gaussians' not specified!")
          raise Exception("missing parameter")
        if "max_iterations" in options:
          n = int(options.pop("max_iterations"))
        else:
          n = 0

        if len(options) > 0:
          Log.Fatal("Unknown parameters: " + str(options))
          raise Exception("unknown parameters")

        # Create the Gaussian Mixture Model.
        model = SGMM(g)
        model.set_features(dataFeat)
        with totalTimer:
          model.train_em(1e-9, n, 1e-9)
      except Exception as e:
        Log.Info("Exception: " + str(e))
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunGMMShogun, self.timeout)

  '''
  Perform Gaussian Mixture Model. If the method has been successfully
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform GMM.", self.verbose)

    results = self.GMMShogun(options)
    if results < 0:
      return results

    return {'Runtime' : results}
