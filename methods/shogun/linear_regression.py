'''
  @file linear_regression.py
  @author Marcus Edel

  Linear Regression with shogun.
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
from shogun.Features import RegressionLabels, RealFeatures
from shogun.Regression import LeastSquaresRegression

'''
This class implements the Linear Regression benchmark.
'''
class LinearRegression(object):

  ''' 
  Create the Linear Regression benchmark instance.
  
  @param dataset - Input dataset to perform Linear Regression on.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, verbose=True): 
    self.verbose = verbose
    self.dataset = dataset

  '''
  Use the shogun libary to implement Linear Regression.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def LinearRegressionShogun(self, options):
    totalTimer = Timer()

    # Load input dataset.
    # If the dataset contains two files then the second file is the responses
    # file. In this case we add this to the command line.
    Log.Info("Loading dataset", self.verbose)
    if len(self.dataset) == 2:
      X = np.genfromtxt(self.dataset[0], delimiter=',')
      y = np.genfromtxt(self.dataset[1], delimiter=',')
    else:
      X = np.genfromtxt(self.dataset, delimiter=',')
      y = X[:, (X.shape[1] - 1)]
      X = X[:,:-1]

    with totalTimer:
      # Perform linear regression.
      model = LeastSquaresRegression(RealFeatures(X.T), RegressionLabels(y))
      model.train()
      b = model.get_w()

    return totalTimer.ElapsedTime()

  '''
  Perform Linear Regression. If the method has been successfully 
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def RunMethod(self, options):
    Log.Info("Perform Linear Regression.", self.verbose)

    return self.LinearRegressionShogun(options)
