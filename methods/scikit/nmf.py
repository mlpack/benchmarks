'''
  @file nmf.py
  @author Marcus Edel

  Non-negative Matrix Factorization with scikit.
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
from sklearn.decomposition import NMF as ScikitNMF

'''
This class implements the Non-negative Matrix Factorization benchmark.
'''
class NMF(object):

  ''' 
  Create the Naive Bayes Classifier benchmark instance.
  
  @param dataset - Input dataset to perform NBC on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout

  '''
  Use the scikit libary to implement Non-negative Matrix Factorization.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def NMFScikit(self, options):

    @timeout(self.timeout, os.strerror(errno.ETIMEDOUT))
    def RunNMFScikit():
      totalTimer = Timer()

      # Load input dataset.
      Log.Info("Loading dataset", self.verbose)
      data = np.genfromtxt(self.dataset, delimiter=',')

      with totalTimer:      
        # Gather parameters.
        seed = re.search("-s (\d+)", options)
        maxIterations = re.search("-m (\d+)", options)
        minResidue = re.search("-e ([^\s]+)", options)
        updateRule = re.search("-u ([^\s]+)", options)

        m = 10000 if not maxIterations else int(maxIterations.group(1))
        e = 1e-05 if not maxIterations else int(minResidue.group(1))

        if updateRule:
          u = updateRule.group(1)
          if u != 'alspgrad':
            Log.Fatal("Invalid update rules ('" + u + "'); must be 'alspgrad'.")
            return -1

        # Perform NMF with the specified update rules.
        if seed:
          s = int(seed.group(1))
          model = ScikitNMF(n_components=2, init='random', max_iter = m, tol = e, random_state = s)
        else:
          model = ScikitNMF(n_components=2, init='nndsvdar', max_iter = m, tol = e)

        W = model.fit_transform(data)
        H = model.components_

      return totalTimer.ElapsedTime()

    try:
      return RunNMFScikit()
    except TimeoutError as e:
      Log.Warn("Script timed out after " + str(self.timeout) + " seconds")
      return -2

  '''
  Perform Non-negative Matrix Factorization. If the method has been successfully 
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def RunMethod(self, options):
    Log.Info("Perform NMF.", self.verbose)

    return self.NMFScikit(options)
