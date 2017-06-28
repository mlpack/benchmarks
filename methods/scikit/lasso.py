'''
  @file lasso.py
  @author Youssef Emad El-Din

  Lasso Regression with scikit.
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
from sklearn.linear_model import Lasso

'''
This class implements the Lasso Regression benchmark.
'''
class LASSO(object):

  '''
  Create the Lasso Regression benchmark instance.

  @param dataset - Input dataset to perform Least Angle Regression on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout

  '''
  Use the scikit libary to implement Lasso Regression.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def LASSOScikit(self, options):
    def RunLASSOScikit(q):
      totalTimer = Timer()

      # Load input dataset.
      Log.Info("Loading dataset", self.verbose)
      inputData = np.genfromtxt(self.dataset[0], delimiter=',')
      responsesData = np.genfromtxt(self.dataset[1], delimiter=',')

      # Get all the parameters.
      if len(options) > 0:
        Log.Fatal("Unknown parameters: " + str(options))
        raise Exception("unknown parameters")

      try:
        with totalTimer:
          # Perform LASSO.
          model = Lasso()
          model.fit(inputData, responsesData)
          out = model.coef_
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunLASSOScikit, self.timeout)

  '''
  Perform Lasso Regression. If the method has been successfully completed
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform LASSO.", self.verbose)

    if len(self.dataset) < 2:
      Log.Fatal("This method requires two datasets.")
      return -1

    results = self.LASSOScikit(options)
    if results < 0:
      return results

    return {'Runtime' : results}
