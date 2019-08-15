'''
  @file linear_regression.py
  @author Marcus Edel

  Class to benchmark the matlab Linear Regression method.
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
This class implements the Linear Regression benchmark.
'''
class MATLAB_LINEARREGRESSION(object):
  def __init__(self, method_param, run_param):
    # Assemble run command.
    dataset = method_param["datasets"]

    if len(dataset) == 2:
      inputCmd = "-i " + dataset[0] + " -t " + dataset[1]
    else:
      inputCmd = "-i " + dataset[0] + " "

    # Split the command using shell-like syntax.
    self.cmd = shlex.split(run_param["matlab_path"] +
      "matlab -nodisplay -nosplash -r \"try, " + "LINEAR_REGRESSION('" +
      inputCmd + "'), catch, exit(1), end, exit(0)\"")

    self.info = "MATLAB_LINEARREGRESSION (" + str(self.cmd) + ")"
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

    return metric
