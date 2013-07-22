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
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, verbose=True): 
    self.verbose = verbose
    self.dataset = dataset

  '''
  Use the scikit libary to implement independent component analysis.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def ICAScikit(self, options):
    totalTimer = Timer()

    # Load input dataset.
    data = np.genfromtxt(self.dataset, delimiter=',')

    s = re.search('-s (\d+)', options)
    s = 0 if not s else int(s.group(1))

    # Perform ICA.
    with totalTimer:
      model = FastICA(random_state=s)
      ic = model.fit(data).transform(data)
      mixing = model.get_mixing_matrix()

    return totalTimer.ElapsedTime()

  '''
  Perform independent component analysis. If the method has been successfully 
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def RunMethod(self, options):
    Log.Info("Perform ICA.", self.verbose)

    return self.ICAScikit(options)
