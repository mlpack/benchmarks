'''
  file lmnn.py
  @author Manish Kumar

  Large Margin Nearest Neighbors with shogun.
'''

import os
import sys
import inspect
import timeout_decorator

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

#Import the metrics definitions path.
metrics_folder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../metrics")))
if metrics_folder not in sys.path:
  sys.path.insert(0, metrics_folder)

from log import *
from timer import *
from definitions import *
from misc import *

import numpy as np
from modshogun import RealFeatures
from modshogun import MulticlassLabels
from modshogun import LMNN as ShogunLMNN

'''
This class implements the Large Margin Nearest Neighbors benchmark.
'''
class LMNN(object):

  '''
  Create the Large Margin Nearest Neighbors instance.

  @param dataset - Input dataset to perform LMNN on.
  @param timeout - The time until the timeout. Default no timeout.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.timeout = timeout
    self.k = 1

  '''
  Use the shogun libary to implement Large Margin Nearest Neighbors.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def LMNNShogun(self, options):
    @timeout_decorator.timeout(self.timeout)
    def RunLMNNShogun():
      totalTimer = Timer()

      # Load input dataset.
      Log.Info("Loading dataset", self.verbose)
      # Use the last row of the training set as the responses.
      X, y = SplitTrainData(self.dataset)
      try:
        feat = RealFeatures(X.T)
        labels = MulticlassLabels(y.astype(np.float64))

        with totalTimer:
          # Get the options for running LMNN.
          if "k" in options:
            self.k = int(options.pop("k"))

          if "maxiter" in options:
            n = int(options.pop("maxiter"))
          else:
            n = 2000

          if len(options) > 0:
            Log.Fatal("Unknown parameters: " + str(options))
            raise Exception("unknown parameters")

          # Perform LMNN.
          prep = ShogunLMNN(feat, labels, self.k)
          prep.set_maxiter(n)
          prep.train()
      except Exception as e:
        return [-1, -1]

      time = totalTimer.ElapsedTime()

      # Get distance.
      distance = prep.get_linear_transform()
      dataList = [X, y]
      accuracy1NN = Metrics.KNNAccuracy(distance, dataList, 1, False)
      accuracy3NN = Metrics.KNNAccuracy(distance, dataList, 3, False)
      accuracy3NNDW = Metrics.KNNAccuracy(distance, dataList, 3, True)
      accuracy5NN = Metrics.KNNAccuracy(distance, dataList, 5, False)
      accuracy5NNDW = Metrics.KNNAccuracy(distance, dataList, 5, True)

      return [time, accuracy1NN, accuracy3NN, accuracy3NNDW,
          accuracy5NN, accuracy5NNDW]

    try:
      return RunLMNNShogun()
    except timeout_decorator.TimeoutError:
      return [-1, -1]

  '''
  Perform Large Margin Nearest Neighbors. If the method has been successfully
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform LMNN.", self.verbose)

    results = self.LMNNShogun(options)
    if results[0] < 0:
      return results[0]

    # Datastructure to store the results.
    metrics = {}
    metrics['Runtime'] = results[0]
    metrics['Accuracy_1_NN'] = results[1]
    metrics['Accuracy_3_NN'] = results[2]
    metrics['Accuracy_3_NN_DW'] = results[3]
    metrics['Accuracy_5_NN'] = results[4]
    metrics['Accuracy_5_NN_DW'] = results[5]

    return metrics

