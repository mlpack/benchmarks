'''
  @file dtc.py
  Class to benchmark the weka Decision Stump Classifier method.
'''

import os, sys, inspect, shlex, subprocess

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *

'''
This class implements the Decision Stump Classifier benchmark.
'''
class WEKA_DECISSIONSTUMP(object):
  def __init__(self, method_param, run_param):
    # Assemble run command.
    self.dataset = check_dataset(method_param["datasets"], ["arff"])

    self.cmd = shlex.split("java -classpath " + run_param["weka_path"] +
      "/weka.jar" + ":methods/weka" + " DECISIONSTUMP -t " + self.dataset[0] +
      " -T " + self.dataset[1])

    self.info = "WEKA_DECISSIONSTUMP (" + str(self.cmd) + ")"
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
      metric['runtime'] = timer["total_time"]

    if len(self.dataset) >= 3:
        predictions = load_dataset("weka_predicted.csv", ["csv"])[0]
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
