'''
  @file lasso.py
  Class to benchmark the matlab lasso method.
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
This class implements the Lasso benchmark.
'''
class MATLAB_LASSO(object):
  def __init__(self, method_param, run_param):
    # Assemble run command.
    dataset = method_param["datasets"]

    opts = {}
    opts["tol"] = 1e-4
    if "tolerance" in method_param:
      opts["tol"] = float(method_param["tolerance"])
    opts["max_iter"] = 1e5
    if "max_iterations" in method_param:
      opts["max_iter"] = int(method_param["max_iterations"])
    opts["alpha"] = 1
    if "alpha" in method_param:
      opts["alpha"] = float(method_param["alpha"])

    inputCmd = "-t " + dataset[0] + " -T " + dataset[1] + " -m " + str(
      opts["max_iter"]) + " -tol " + str(opts["tol"]) + " -a " + str(
      opts["alpha"])

    self.cmd = shlex.split(run_param["matlab_path"] +
      "matlab -nodisplay -nosplash -r \"try, LASSO('" + inputCmd +
      "'), catch, exit(1), end, exit(0)\"")

    self.info = "MATLAB_LASSO (" + str(self.cmd) + ")"
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
