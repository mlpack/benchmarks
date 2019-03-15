'''
  @file lda.py
  @author Chirag Pabbaraju

  Linear Discriminant Analysis for Multiclass classification with shogun.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from shogun import MCLDA, RealFeatures, MulticlassLabels

'''
This class implements the Linear Discriminant Analysis benchmark.
'''
class SHOGUN_LDA(object):
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_LDA ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    if "tolerance" in method_param:
      self.tolerance = float(method_param["tolerance"])
    if "store" in method_param:
      self.store = bool(method_param["store"])

    distinct_labels = list(set(self.data_split[1]))
    mapping = {}
    self.reverseMapping = {}
    idx = 0
    for label in distinct_labels:
      mapping[label] = idx
      self.reverseMapping[idx] = label
      idx += 1
    for i in range(len(self.data_split[1])):
      self.data_split[1][i] = mapping[self.data_split[1][i]]

    self.train_feat = RealFeatures(self.data_split[0].T)
    self.train_labels = MulticlassLabels(self.data_split[1])
    self.test_feat = RealFeatures(self.data[1].T)

  def __str__(self):
    return self.info

  def metric(self):
    totalTimer = Timer()
    with totalTimer:
      model = MCLDA(self.train_feat, self.train_labels, self.tolerance,
        self.store)
      model.train()

      if len(self.data) > 1:
        predictions = model.apply_multiclass(self.test_feat).get_labels()
        # reverse map the predicted labels to actual labels
        for i in range(len(predictions)):
          predictions[i] = self.reverseMapping[predictions[i]]

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    if len(self.data) >= 2:
      confusionMatrix = Metrics.ConfusionMatrix(self.data[1], predictions)
      metric['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metric['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metric['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metric['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metric['MSE'] = Metrics.SimpleMeanSquaredError(self.data[1], predictions)

    return metric
