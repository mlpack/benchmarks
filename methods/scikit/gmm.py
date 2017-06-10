'''
  @file gmm.py
  @author Marcus Edel

  Gaussian Mixture Model with scikit.
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
from sklearn import mixture

'''
This class implements the Gaussian Mixture Model benchmark.
'''
class GMM(object):

  '''
  Create the Gaussian Mixture Model benchmark instance.

  @param dataset - Input dataset to perform Gaussian Mixture Model on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout

  '''
  Use the scikit libary to implement Gaussian Mixture Model.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def GMMScikit(self, options):
    def RunGMMScikit(q):
      totalTimer = Timer()

      # Load input dataset.
      dataPoints = np.genfromtxt(self.dataset, delimiter=',')

      # Get all the parameters.
      g = re.search("-g (\d+)", options)
      s = re.search("-s (\d+)", options)
      tol = re.search("-T (\d+)", options)
      n_init = re.search("-t (\d+)", options)
      max_iter = re.search("-n (\d+)", options)
      g = 1 if not g else int(g.group(1))
      s = 0 if not s else int(s.group(1))
      tol = 0.001 if not tol else float(tol.group(1))
      max_iter = 100 if not max_iter else int(max_iter.group(1))
      n_init = 1 if not n_init else int(n_init.group(1))

      try:
        # Create the Gaussian Mixture Model
	      # Some params changed to match mlpack defaults.
        model = mixture.GaussianMixture(n_components=g,
                                        random_state=s,
                                        n_init=n_init,
                                        tol=tol,
					max_iter = max_iter)
        with totalTimer:
          model.fit(dataPoints)
      except Exception as e:
        q.put(-1)
        return -1

      time = totalTimer.ElapsedTime()
      q.put(time)
      return time

    return timeout(RunGMMScikit, self.timeout)

  '''
  Perform Gaussian Mixture Model. If the method has been successfully completed
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform GMM.", self.verbose)

    results = self.GMMScikit(options)
    if results < 0:
      return results

    return {'Runtime' : results}
