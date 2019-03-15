'''
  @file svr.py
  Class to benchmark the R SVR method.
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
This class implements the SVR benchmark.
'''
class R_SVR(object):
  def __init__(self, method_param, run_param):
    # Assemble run model parameter.
    self.dataset = method_param["datasets"]

    opts = {}
    opts["kernel"] = 'radial'
    if "kernel" in method_param:
      opts["kernel"] = str(method_param["kernel"])
    opts["C"] = 1.0
    if "c" in method_param:
      opts["C"] = float(method_param["c"])
    opts["epsilon"] = 1.0
    if "epsilon" in method_param:
      opts["epsilon"] = float(method_param["epsilon"])
    opts["gamma"] = 0.1
    if "gamma" in method_param:
      opts["gamma"] = float(method_param["gamma"])

    self.cmd = shlex.split("libraries/bin/Rscript " + run_param["r_path"] +
      "svr.r" + " -t " + self.dataset[0] + " -k " + opts['kernel'] + " -c " +
      str(opts["C"]) + " -e " + str(opts["epsilon"]) + " -g " +
      str(opts["gamma"]))

    self.info = "R_SVR ("  + str(self.cmd) +  ")"
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

    return metric
