'''
  @file lars.py
  @author Marcus Edel

  Least Angle Regression with mlpy.
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
This class implements the Least Angle Regression benchmark.
'''
class LARS(object):

  ''' 
  Create the Least Angle Regression benchmark instance.
  
  @param dataset - Input dataset to perform Least Angle Regression on.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, verbose=True): 
    self.verbose = verbose
    self.dataset = dataset

  '''
  Use the mlpy libary to implement Least Angle Regression.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def LARSMlpy(self, options):
    totalTimer = Timer()

    # Load input dataset.
    Log.Info("Loading dataset", self.verbose)
    inputData = np.genfromtxt(self.dataset[0], delimiter=',')
    responsesData = np.genfromtxt(self.dataset[1], delimiter=',')

    with totalTimer:
      # Perform LARS.
      model = mlpy.LARS()
      model.learn(inputData, responsesData)
      out = model.beta()

    return totalTimer.ElapsedTime()

  '''
  Perform Least Angle Regression. If the method has been successfully completed 
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def RunMethod(self, options):
    Log.Info("Perform LARS.", self.verbose)

    if len(self.dataset) != 2:
      Log.Fatal("This method requires two datasets.")
      return -1

    return self.LARSMlpy(options)
