"""
  @file decision_tree.py
  @author Xu Kaiqiang

  Class to benchmark the mlpack decision tree classification method.
  Here I'd like to clarify more info on this benchmark.
  Usually, this file will be give parameters such as train_dataset(including
  labels as last column), test_dataset, test_labels, which are stored in
  self.dataset.
"""

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *

"""
This class implements the Decision Tree Classifier benchmark.
"""
class MLPACK_DTC(object):
  def __init__(self, method_param, run_param):
    # Assemble run command.
    self.dataset = check_dataset(method_param["datasets"], ["csv"])

    self.cmd = shlex.split(run_param["mlpack_path"] +
        "mlpack_decision_tree -t " + self.dataset[0] + " -T " +
        self.dataset[1] + " -v " + " -p " + " mlpack_dct_predict.csv")

    self.info = "MLPACK_DTC (" + str(self.cmd) + ")"
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
    timer = parse_timer(self.output)
    if timer:
      metric["runtime"] = timer["total_time"] - timer["loading_data"] - timer["saving_data"]

    if len(self.dataset) >= 3:
        predictions = load_dataset("mlpack_dct_predict.csv", ["csv"])[0]
        true_labels = load_dataset(self.dataset[2], ["csv"])[0]

        confusionMatrix = Metrics.ConfusionMatrix(true_labels, predictions)
        metric['Precision'] = Metrics.AvgPrecision(confusionMatrix)
        metric['Recall'] = Metrics.AvgRecall(confusionMatrix)
        metric['FMeasure'] = Metrics.AvgFMeasure(confusionMatrix)
        metric['Lift'] = Metrics.LiftMultiClass(confusionMatrix)
        metric['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
        metric['Information'] = Metrics.AvgMPIArray(
          confusionMatrix, true_labels, predictions)
        metric['MSE'] = Metrics.SimpleMeanSquaredError(
          true_labels, predictions)

    return metric
