import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
import mlpy

'''
This class implements the Decision Tree Classifier benchmark.
'''
class MLPY_DECISIONTREE(object):
  def __init__(self, method_param, run_param):
    self.info = "MLPY_DECISIONTREE ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.build_opts = {}
    self.build_opts["stumps"] = 0
    if "stumps" in method_param:
      self.build_opts["stumps"] = int(method_param["stumps"])
    self.build_opts["minsize"] = 1
    if "minimum_leaf_size" in method_param:
      self.build_opts["minsize"] = int(method_param["minimum_leaf_size"])

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = mlpy.ClassTree(**self.build_opts)
      model.learn(self.data_split[0], self.data_split[1])

      if len(self.data) >= 2:
        predictions = model.pred(self.data[1])

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
