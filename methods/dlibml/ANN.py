'''
  @file ann.py
  Class to benchmark the ANN method with dlibml.
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
This class implements the ANN benchmark.
'''
class DLIBML_ANN(object):
  def __init__(self, method_param, run_param):
    # Assemble run command.
    self.cmd = run_param["dlibml_path"] + "dlibml_ann"
    if "datasets" in method_param:
      dataset = check_dataset(method_param["datasets"], ["csv", "txt"])
      if len(dataset) == 2:
        self.cmd += " -r " + dataset[0] + " -q " + dataset[1]
      elif len(dataset) == 1:
        self.cmd += " -r " + dataset[0]
    if "k" in method_param:
      self.cmd += " -k " + str(method_param["k"])
    if "num" in method_param:
      self.cmd += " -n " + str(method_param["num"])
    if "sample_pct" in method_param:
      self.cmd += " -s " + str(method_param["sample_pct"])
    self.cmd += " -v"

    self.info = "DLIBML_ANN (" + self.cmd + ")"
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
      metric["runtime"] = timer["Nearest_Neighbors"]

    return metric
