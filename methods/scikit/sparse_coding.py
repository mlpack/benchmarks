'''
  @file sparse_coding.py
  @author Marcus Edel

  Sparse Coding with scikit.
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
from sklearn.decomposition import SparseCoder

'''
This class implements the Sparse Coding benchmark.
'''
class SparseCoding(object):

  ''' 
  Create the Sparse Coding benchmark instance.
  
  @param dataset - Input dataset to perform Sparse Coding on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout

  '''
  Use the scikit libary to implement Sparse Coding.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def SparseCodingScikit(self, options):
    def RunSparseCodingScikit(q):
      totalTimer = Timer()

      # Load input dataset.
      inputData = np.genfromtxt(self.dataset[0], delimiter=',')
      dictionary = np.genfromtxt(self.dataset[1], delimiter=',')

      # Get all the parameters.
      l = re.search("-l (\d+)", options)
      l = 0 if not l else int(l.group(1))

      with totalTimer:
        # Perform Sparse Coding.
        model = SparseCoder(dictionary=dictionary, transform_algorithm='lars',
            transform_alpha=l)
        code = model.transform(inputData)

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunSparseCodingScikit, self.timeout)

  '''
  Perform Sparse Coding. If the method has been successfully completed 
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def RunMethod(self, options):
    Log.Info("Perform Sparse Coding.", self.verbose)

    if len(self.dataset) != 2:
      Log.Fatal("This method requires two datasets.")
      return -1

    return self.SparseCodingScikit(options)
