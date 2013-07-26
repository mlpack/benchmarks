'''
  @file kernel_pca.py
  @author Marcus Edel

  Kernel Principal Components Analysis with shogun.
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
from shogun.Features import RealFeatures
from shogun.Classifier import KernelPCA
from shogun.Kernel import GaussianKernel, PolyKernel, LinearKernel, SigmoidKernel

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
  Use the shogun libary to implement Kernel Principal Components Analysis.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def KPCAShogun(self, options):

    @timeout(self.timeout, os.strerror(errno.ETIMEDOUT))
    def RunKPCAShogun():
      totalTimer = Timer()

      # Load input dataset.
      Log.Info("Loading dataset", self.verbose)
      data = np.genfromtxt(self.dataset, delimiter=',')
      dataFeat = RealFeatures(data.T)

      with totalTimer:
        # Get the new dimensionality, if it is necessary.
        dimension = re.search('-d (\d+)', options)
        if not dimension:
          d = data.shape[1]
        else:
          d = int(dimension.group(1))      
          if (d > data.shape[1]):
            Log.Fatal("New dimensionality (" + str(d) + ") cannot be greater "
              + "than existing dimensionality (" + str(data.shape[1]) + ")!")
            return -1    

        # Get the kernel type and make sure it is valid.
        kernel = re.search("-k ([^\s]+)", options)
        if not kernel:
            Log.Fatal("Choose kernel type, valid choices are 'linear', 'hyptan'" + 
                  ", 'polynomial' and 'gaussian'.")
            return -1
        elif kernel.group(1) == "polynomial":
          degree = re.search('-D (\d+)', options)
          degree = 1 if not degree else int(degree.group(1))
          
          kernel = PolyKernel(dataFeat, dataFeat, degree, True)
        elif kernel.group(1) == "gaussian":
          kernel = GaussianKernel(dataFeat, dataFeat, 2.0)
        elif kernel.group(1) == "linear":
          kernel = LinearKernel(dataFeat, dataFeat)
        elif kernel.group(1) == "hyptan":
          kernel = SigmoidKernel(dataFeat, dataFeat, 2, 1.0, 1.0)
        else:
          Log.Fatal("Invalid kernel type (" + kernel.group(1) + "); valid choices"
                  + " are 'linear', 'hyptan', 'polynomial' and 'gaussian'.")
          return -1

        # Perform Kernel Principal Components Analysis.
        model = KernelPCA(kernel)
        model.set_target_dim(d)
        model.init(dataFeat)
        model.apply_to_feature_matrix(dataFeat)

      return totalTimer.ElapsedTime()

    try:
      return RunKPCAShogun()
    except TimeoutError as e:
      Log.Warn("Script timed out after " + str(self.timeout) + " seconds")
      return -2    

  '''
  Perform Kernel Principal Components Analysis. If the method has been 
  successfully completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def RunMethod(self, options):
    Log.Info("Perform KPCA.", self.verbose)

    return self.KPCAShogun(options)
