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
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, verbose=True): 
    self.verbose = verbose
    self.dataset = dataset

  '''
  Destructor to clean up at the end.
  '''
  def __del__(self):
    pass

  '''
  Use the mlpy libary to implement Kernel Principal Components Analysis.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def KPCAMlpy(self, options):
    totalTimer = Timer()

    # Load input dataset.
    Log.Info("Loading dataset", self.verbose)
    data = np.genfromtxt(self.dataset, delimiter=',')

    with totalTimer:
      # Get the new dimensionality, if it is necessary.
      dimension = re.search('-d (\d+)', options)
      if not dimension:
        d = data.shape[0]
      else:
        d = int(dimension.group(1))      
        if (d > data.shape[1]):
          Log.Fatal("New dimensionality (" + str(d) + ") cannot be greater "
            + "than existing dimensionality (" + str(data.shape[1]) + ")!")
          return -1    

      # Get the kernel type and make sure it is valid.
      kernel = re.search("-k ([^\s]+)", options)
      if not kernel:
          Log.Fatal("Choose kernel type, valid choices are 'polynomial', " + 
                "'gaussian', 'linear' and 'hyptan'.")
          return -1
      elif kernel.group(1) == "polynomial":
        degree = re.search('-D (\d+)', options)
        if not degree:
          degree = 1
        else:
          degree = int(degree.group(1))
        
        kernel = mlpy.kernel_polynomial(data, data, d=degree)
      elif kernel.group(1) == "gaussian":
        kernel = mlpy.kernel_gaussian(data, data, sigma=2) 
      elif kernel.group(1) == "linear":
        kernel = mlpy.kernel_linear(data, data)
      elif kernel.group(1) == "hyptan":
        kernel = mlpy.kernel_sigmoid(data, data)
      else:
        Log.Fatal("Invalid kernel type (" + kernel.group(1) + "); valid " +
                "choices are 'polynomial', 'gaussian', 'linear' and 'hyptan'.")
        return -1

      # Perform Kernel Principal Components Analysis.
      model = mlpy.KPCA()
      model.learn(kernel)
      out = model.transform(kernel, k=d)

    return totalTimer.ElapsedTime()

  '''
  Perform Kernel Principal Components Analysis. If the method has been 
  successfully completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def RunMethod(self, options):
    Log.Info("Perform KPCA.", self.verbose)

    return self.KPCAMlpy(options)
