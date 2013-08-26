'''
  @file pca.py
  @author Marcus Edel

  Principal Components Analysis with shogun.
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
from shogun.Classifier import PCA as ShogunPCA

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

    # Load input dataset.
    Log.Info("Loading dataset", verbose)
    self.data = np.genfromtxt(dataset, delimiter=',')

  '''
  Use the shogun libary to implement Principal Components Analysis.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def PCAShogun(self, options):
    def RunPCAShogun(q):
      totalTimer = Timer()
      
      # Load input dataset.
      Log.Info("Loading dataset", self.verbose)
      feat = RealFeatures(self.data.T)

      try:
        with totalTimer:
          # Find out what dimension we want.
          match = re.search('-d (\d+)', options)

          if not match:
            k = self.data.shape[1]
          else:
            k = int(match.group(1))      
            if (k > self.data.shape[1]):
              Log.Fatal("New dimensionality (" + str(k) + ") cannot be greater than"
                  + "existing dimensionality (" + str(self.data.shape[1]) + ")!")
              q.put(-1)
              return -1

          # Get the options for running PCA.
          s = True if options.find("-s") > -1 else False

          # Perform PCA.
          prep = ShogunPCA(s)
          prep.set_target_dim(k)
          prep.init(feat)
          prep.apply_to_feature_matrix(feat)
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunPCAShogun, self.timeout)

  '''
  Perform Principal Components Analysis. If the method has been successfully 
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def RunMethod(self, options):
    Log.Info("Perform PCA.", self.verbose)

    return self.PCAShogun(options)
