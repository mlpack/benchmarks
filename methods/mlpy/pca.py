'''
  @file pca.py
  @author Marcus Edel

  Principal Components Analysis with mlpy.
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
  Use the mlpy libary to implement Principal Components Analysis.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not 
  successful.
  '''
  def PCAMlpy(self, options):
    def RunPCAMlpy(q):
      totalTimer = Timer()

      # Load input dataset.
      Log.Info("Loading dataset", self.verbose)
      data = np.genfromtxt(self.dataset, delimiter=',')

      try:
        with totalTimer:
          # Find out what dimension we want.
          match = re.search('-d (\d+)', options)

          if not match:
            k = data.shape[1]
          else:
            k = int(match.group(1))      
            if (k > data.shape[1]):
              Log.Fatal("New dimensionality (" + str(k) + ") cannot be greater "
                  + "than existing dimensionality (" + str(data.shape[1]) + ")!")
              q.put(-1)
              return -1

          # Get the options for running PCA.
          s = True if options.find("-s") > -1 else False

          # Perform PCA.
          prep = mlpy.PCA(whiten=s)
          prep.learn(data)
          out = prep.transform(data, k)      
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunPCAMlpy, self.timeout)

  '''
  Perform Principal Components Analysis. If the method has been successfully 
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not 
  successful.
  '''
  def RunMethod(self, options):
    Log.Info("Perform PCA.", self.verbose)

    return self.PCAMlpy(options)
