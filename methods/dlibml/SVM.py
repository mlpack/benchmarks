'''
  @file svm.py
  Class to benchmark the SVM method with dlib-ml.
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
This class implements the SVM benchmark.
'''
class DLIBML_SVM(object):
  def __init__(self, method_param, run_param):
    # Assemble run command.
    self.cmd = run_param["dlibml_path"] + "dlibml_svm"
    if "datasets" in method_param:
      self.dataset = check_dataset(method_param["datasets"], ["csv", "txt"])
      self.cmd += " -t " + self.dataset[0] + " -T " + self.dataset[1]

    if "kernel" in method_param:
      self.cmd += " -k " + str(method_param["kernel"])
    else:
      self.cmd += " -k " + "rbf"

    if "C" in method_param:
      self.cmd += " -c " + str(method_param["C"])
    else:
      self.cmd += " -c " + "0.1"

    if "coef" in method_param:
      self.cmd += " -g " + str(method_param["coef"])
    else:
      self.cmd += " -g " + "1"

    if "degree" in method_param:
      self.cmd += " -d " + str(method_param["degree"])
    else:
      self.cmd += " -d " + "2"
    self.cmd += " -v"

    self.info = "DLIBML_SVM (" + self.cmd + ")"
    self.timeout = run_param["timeout"]

  def __str__(self):
    return self.info

  def metric(self):
    try:
      output = subprocess.check_output(self.cmd, stderr=subprocess.STDOUT,
        shell=True, timeout=self.timeout)
    except subprocess.TimeoutExpired as e:
      raise Exception("method timeout")
    except Exception as e:
      raise Exception(str(e))

    metric = {}
    timer = parse_timer(output)
    if timer:
      metric["runtime"] = timer["runtime"]

    if len(self.dataset) > 2:
      predictions = load_dataset("predictions.csv", ["csv"])[0]
      true_labels = load_dataset(self.dataset[2], ["csv"])[0]

      confusionMatrix = Metrics.ConfusionMatrix(true_labels, predictions)
      metric['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metric['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metric['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metric['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metric['MSE'] = Metrics.SimpleMeanSquaredError(true_labels, predictions)

    return metric
