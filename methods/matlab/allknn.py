'''
  @file allknn.py
  @author Marcus Edel

  Class to benchmark the matlab All K-Nearest-Neighbors method.
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
This class implements the All K-Nearest-Neighbors benchmark.
'''
class MATLAB_ALLKNN(object):
  def __init__(self, method_param, run_param):
    # Assemble run command.
    dataset = check_dataset(method_param["datasets"], ["csv", "txt"])

    self.cmd = ""
    if "k" in method_param:
      self.cmd += " -k " + str(method_param["k"])
    if "seed" in method_param:
      self.cmd += " -s " + str(method_param["seed"])
    if "naive_mode" in method_param:
      self.cmd += " -N"
    if "leaf_size" in method_param:
      self.cmd += " -l " + str(method_param["leaf_size"])

    if len(dataset) == 2:
      self.cmd = "-r " + dataset[0] + " -q " + dataset[1] + " " \
          + self.cmd
    else:
      self.cmd = "-r " + dataset[0] + " " + self.cmd

    self.cmd = shlex.split(run_param["matlab_path"] +
      "matlab -nodisplay -nosplash -r \"try, " + "ALLKNN('"  +
      self.cmd + "'), catch, exit(1), end, exit(0)\"")

    self.info = "MATLAB_ALLKNN (" + str(self.cmd) + ")"
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
