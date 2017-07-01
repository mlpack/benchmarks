'''
  @file SVR.py
  @author Saurabh Mahindre

  SVR Regression with shogun.
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
from misc import *

import numpy as np
from modshogun import RegressionLabels, RealFeatures
from modshogun import LibSVR
from modshogun import GaussianKernel

'''
This class implements the SVR Regression benchmark.
'''
class SVR(object):

  '''
  Create the SVR Regression benchmark instance.

  @param dataset - Input dataset to perform SVR Regression on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.C = 1.0
    self.epsilon=1.0
    self.width = 10.0

  '''
  Use the shogun libary to implement Linear Regression.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def SVRShogun(self, options):
    def RunSVRShogun(q):
      totalTimer = Timer()
      # Load input dataset.
      Log.Info("Loading dataset", self.verbose)
      # Use the last row of the training set as the responses.
      X, y = SplitTrainData(self.dataset)

      # Get all the parameters.
      self.C = 1.0
      self.epsilon = 1.0
      self.width = 0.1
      if "c" in options:
        self.C = float(options.pop("c"))
      if "epsilon" in options:
        self.epsilon = float(options.pop("epsilon"))
      if "gamma" in options:
        self.width = np.true_divide(1, float(options.pop("gamma")))

      if len(options) > 0:
        Log.Fatal("Unknown parameters: " + str(options))
        raise Exception("unknown parameters")

      data = RealFeatures(X.T)
      labels_train = RegressionLabels(y)
      self.kernel = GaussianKernel(data, data, self.width)

      try:
        with totalTimer:
          # Perform SVR.
          model = LibSVR(self.C, self.epsilon, self.kernel, labels_train)
          model.train()
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunSVRShogun, self.timeout)

  '''
  Perform SVR Regression. If the method has been successfully completed
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform SVR Regression.", self.verbose)

    results = self.SVRShogun(options)
    if results < 0:
      return results

    return {'Runtime' : results}
