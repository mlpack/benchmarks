'''
  @file svr.py
  Class to benchmark the matlab Support Vector Regression method.
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
This class implements the Support Vector Regression benchmark.
'''
class MATLAB_SVR(object):
  def __init__(self, method_param, run_param):
    # Assemble run command.
    self.dataset = method_param["datasets"]

    self.opts = {}
    self.opts["kernel"] = 'rbf'
    if "kernel" in method_param:
      self.opts["kernel"] = str(method_param["kernel"])
    self.opts["max_iter"] = 1000
    if "max_iterations" in method_param:
      self.opts["max_iter"] = int(method_param["max_iterations"])
    self.opts["epsilon"] = 1.0
    if "epsilon" in method_param:
      self.opts["epsilon"] = float(method_param["epsilon"])

    inputCmd = "-t " + self.dataset[0] + " -T " + self.dataset[1] + " -k " + \
    self.opts["kernel"] + " --max_iter "+ str(self.opts["max_iter"])
    self.cmd = shlex.split(run_param["matlab_path"] +
      "matlab -nodisplay -nosplash -r \"try, SVR('" + inputCmd +
      "'), catch, exit(1), end, exit(0)\"")

    self.info = "MATLAB_SVR (" + str(self.cmd) + ")"
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
      metric["runtime"] = timer["total_time"]

      if len(self.dataset) > 2:
        predictions = load_dataset("predictions.csv", ["csv"])[0]
        true_labels = load_dataset(self.dataset[2], ["csv"])[0]
        metric['MSE'] = Metrics.SimpleMeanSquaredError(true_labels, predictions)

    return metric
