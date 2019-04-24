'''
  @file dtc.py
  @author Saurabh Mahindre
  @contributor Rukmangadh Sai Myana

  Classifier implementing the CART (decision tree) classifier with shogun.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from shogun import RealFeatures, MulticlassLabels, CARTree, PT_MULTICLASS

'''
This class implements the decision tree classifier benchmark for Multi-class
classification.

Notes
-----
The following are the configurable options provided by this benchmark:
* pruning: True, False
* k: The number of folds in k-fold cross validation when pruning is set to True
'''
class SHOGUN_DTC(object):

  '''
  Create the CART Tree Classification benchmark instance.

  @type method_param - dict
  @param method_paramm - Extra options for the benchmarking method.
  @type run_param - dict
  @param run_param - Path option for executing the benchmark. Not used for
  Shogun.
  '''
  def __init__(self, method_param, run_param):
    self.info = "SHOGUN_DTC ("  + str(method_param) +  ")"

    # Assemble run model parameter.
    self.data = load_dataset(method_param["datasets"], ["csv"])
    self.data_split = split_dataset(self.data[0])

    self.train_feat = RealFeatures(self.data_split[0].T)

	# Encode the labels into {0,1,2,3,......,num_classes-1}
    self.train_labels, self.label_map = label_encoder(self.data_split[1])
    self.train_labels = MulticlassLabels(self.train_labels)

    if len(self.data) >= 2:
      self.test_feat = RealFeatures(self.data[1].T)

    # Flag for Cross Validation Pruning
    self.cv_prune = False
    if "pruning" in method_param:
      self.cv_prune = bool(method_param["pruning"])

    self.num_folds = 2
    if "k" in method_param:
      # Making sure that the value is of the right type
      self.num_folds = int(method_param["k"])

  '''
  Return information about the benchmarking isntance.

  @rtype - str
  @returns - Information as a single string
  '''
  def __str__(self):
    return self.info

  '''
  Calculate metrics to be used for benckmarking.

  @rtype - dict
  @returns - Evaluated metrics.
  '''
  def metric(self):
    totalTimer = Timer()

    with totalTimer:
      model = CARTree(np.array([False] * self.train_feat.get_num_features()), 
        PT_MULTICLASS, self.num_folds, self.cv_prune)

      model.set_labels(self.train_labels)
      model.train(self.train_feat)

      if len(self.data) >= 2:
        predictions = model.apply_multiclass(self.test_feat).get_labels()

    metric = {}
    metric["runtime"] = totalTimer.ElapsedTime()

    if len(self.data) >= 2:
      predictions = label_decoder(predictions, self.label_map)

    if len(self.data) >= 3:
      confusionMatrix = Metrics.ConfusionMatrix(self.data[2], predictions)
      metric['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metric['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metric['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metric['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metric['MSE'] = Metrics.SimpleMeanSquaredError(self.data[2], predictions)

    return metric
