'''
  @file adaboost.py
  @author Marcus Edel

  AdaBoost classifier with scikit.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from sklearn.ensemble import AdaBoostClassifier

'''
This class implements the AdaBoost classifier benchmark.
'''
class SCIKIT_ADABOOST(object):
  def __init__(self, method_param, run_param):
    self.info = "SCIKIT_ADABOOST ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.build_opts = {}
    if "num_estimators" in method_param:
      self.build_opts["n_estimators"] = int(method_param["num_estimators"])
    if "learning_rate" in method_param:
      self.build_opts["learning_rate"] = float(method_param["learning_rate"])
    if "algorithm" in method_param:
      self.build_opts["algorithm"] = str(method_param["algorithm"])
    if "seed" in method_param:
      self.build_opts["random_state"] = int(method_param["seed"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = AdaBoostClassifier(**self.build_opts)
      model.fit(self.data_split[0], self.data_split[1])
      predictions = model.predict(self.data[1])

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
