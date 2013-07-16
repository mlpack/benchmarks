'''
  @file gmm.py
  @author Marcus Edel

  Gaussian Mixture Model with shogun.
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
from shogun import Clustering

'''
This class implements the Gaussian Mixture Model benchmark.
'''
class GMM(object):

  ''' 
  Create the Gaussian Mixture Model benchmark instance.
  
  @param dataset - Input dataset to perform Gaussian Mixture Model on.
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
  Use the shogun libary to implement Gaussian Mixture Model.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def GMMShogun(self, options):
    totalTimer = Timer()

    # Load input dataset.
    dataPoints = np.genfromtxt(self.dataset, delimiter=',')
    dataFeat = RealFeatures(dataPoints.T)

    # Get all the parameters.
    g = re.search("-g (\d+)", options)
    n = re.search("-n (\d+)", options)
    s = re.search("-n (\d+)", options)

    g = 1 if not g else int(g.group(1))
    n = 250 if not n else int(n.group(1))

    # Create the Gaussian Mixture Model.
    model = Clustering.GMM(g)
    model.set_features(dataFeat)
    with totalTimer:
      model.train_em(max_iter=n)

    return totalTimer.ElapsedTime()

  '''
  Perform Gaussian Mixture Model. If the method has been successfully 
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def RunMethod(self, options):
    Log.Info("Perform GMM.", self.verbose)

    return self.GMMShogun(options)
