'''
  @file ica.py
  @author Marcus Edel

  Independent component analysis with scikit.
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
from sklearn.decomposition import FastICA

'''
This class implements the independent component analysis benchmark.
'''
class ICA(object):

  '''
  Create the independent component analysis benchmark instance.

  @param dataset - Input dataset to perform independent component analysis on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout

  '''
  Use the scikit libary to implement independent component analysis.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def ICAScikit(self, options):
    def RunICAScikit(q):
      totalTimer = Timer()

      # Load input dataset.
      data = np.genfromtxt(self.dataset, delimiter=',')

      s = re.search('-s (\d+)', options)
      n_components = re.search('--n_components (\d+)', options)
      algorithm = re.search('--algorithm (\s+)', options)
      fun = re.search('--fun (\s+)', options)
      max_iter = re.search('--max_iter (\d+)', options)
      tol = re.search('--tol (\d+)', options)

      s = 0 if not s else int(s.group(1))
      n_components = None if not n_components else int(n_components.group(1))
      algorithm = 'parallel' if not algorithm else str(algorithm.group(1))
      if algorithm not in ['parallel','deflation']:
          Log.Fatal("Invalid value for algorithm: "+ str(algorithm.group(1))+" .Must be either parallel or deflation")
          q.put(-1)
          return -1
      fun = 'logcosh' if not fun else str(fun.group(1))
      if fun not in ['logcosh','exp','cube']:
          Log.Fatal("Invalid value for fun: "+ str(fun.group(1))+" .Must be either logcosh,exp or cube")
          q.put(-1)
          return -1
      max_iter = 200 if not max_iter else int(max_iter.group(1))
      tol = 0.0001 if not tol else float(tol.group(1))

      try:
        # Perform ICA.
        with totalTimer:
          model = FastICA(n_components = n_components,
                          algorithm = algorithm,
                          fun = fun,
                          max_iter = max_iter,
                          tol = tol,
                          random_state = s)
          ic = model.fit(data).transform(data)
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunICAScikit, self.timeout)

  '''
  Perform independent component analysis. If the method has been successfully
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform ICA.", self.verbose)

    results = self.ICAScikit(options)
    if results < 0:
      return results

    return {'Runtime' : results}
