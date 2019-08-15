'''
  @file random_forest.py
  Class to benchmark the R Random Forest method.
'''

import os, sys, inspect, shlex, subprocess, re

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *

'''
This class implements the Random Forest benchmark.
'''
class R_RANDOMFOREST(object):
  def __init__(self, method_param, run_param):
    # Assemble run model parameter.
    self.dataset = method_param["datasets"]

    self.build_opts = {}
    self.build_opts["n_estimators"] = 500
    if "num_trees" in method_param:
      self.build_opts["n_estimators"] = int(method_param["num_trees"])
    self.build_opts["min_samples_leaf"] = 1
    if "minimum_leaf_size" in method_param:
      self.build_opts["min_samples_leaf"] = int(
        method_param["minimum_leaf_size"])

    self.cmd = shlex.split("libraries/bin/Rscript " + run_param["r_path"] +
      "random_forest.r" + " -t " + self.dataset[0] + " -T " + self.dataset[1] +
      " -n " + str(self.build_opts["n_estimators"]) + " -m " +
      str(self.build_opts["min_samples_leaf"]))

    self.info = "R_RANDOMFOREST ("  + str(self.cmd) +  ")"
    self.timeout = run_param["timeout"]
    self.output = None

  def __str__(self):
    return self.info

  def metric(self):
    try:
      self.output = subprocess.check_output(self.cmd, stderr=subprocess.STDOUT,
        shell=False, timeout=self.timeout)
    except subprocess.TimeoutExpired as e:
      raise Exception("method timeout")
    except Exception as e:
      subprocess_exception(e, self.output)

    metric = {}
    metric["runtime"] = float(re.findall("(\d+\.\d+). *sec elapsed",
      self.output.decode("utf-8"))[0])

    if len(self.dataset) == 3:
      predictions = load_dataset("predictions.csv", ["csv"])[0]
      predictions = predictions[1:]
      true_labels = load_dataset(self.dataset[2], ["csv"])[0]

      confusionMatrix = Metrics.ConfusionMatrix(true_labels, predictions)
      metric['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metric['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metric['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metric['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metric['MSE'] = Metrics.SimpleMeanSquaredError(true_labels, predictions)

    return metric
