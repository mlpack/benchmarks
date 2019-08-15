'''
  @file losgistic_regression.py
  @author Marcus Edel

  Logistic Regression with Milk.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
import milk.supervised.logistic

'''
This class implements the Logistic Regression Classifier benchmark.
'''
class MILK_LOGISTICREGRESSION(object):
  def __init__(self, method_param, run_param):
    self.info = "MILK_LOGISTICREGRESSION ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data)

  def __str__(self):
    return self.info

  def metric(self):
    self.model = milk.supervised.logistic.logistic_learner()

    totalTimer = Timer()
    with totalTimer:
      self.model = self.model.train(self.data_split[0], self.data_split[1])

      if len(self.data) >= 2:
        predictions = np.greater(self.model.apply(self.data[1]), 0.5)

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    if len(self.data) == 3:
      confusionMatrix = Metrics.ConfusionMatrix(self.data[2], predictions)
      metric['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metric['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metric['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metric['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metric['MSE'] = Metrics.SimpleMeanSquaredError(self.data[2], predictions)

    return metric
