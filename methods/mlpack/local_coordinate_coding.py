'''
  @file local_coordinate_coding.py
  @author Marcus Edel

  Class to benchmark the mlpack Local Coordinate Coding method.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *

'''
This class implements the Local Coordinate Coding benchmark.
'''
class MLPACK_LOCALCOORDINATECODING(object):
  def __init__(self, method_param, run_param):
    # Assemble run command.
    self.dataset = check_dataset(method_param["datasets"], ["csv", "txt"])

    options = ""
    if "atoms" in method_param:
      options += " -k " + str(method_param["atoms"])
    if "normalize" in method_param:
      options += " -N"
    if "seed" in method_param:
      options += " --seed " + str(method_param["seed"])

    self.cmd = shlex.split(run_param["mlpack_path"] +
      "mlpack_local_coordinate_coding -t " + self.dataset[0] + " -v " + options)

    self.info = "MLPACK_LOCALCOORDINATECODING (" + str(self.cmd) + ")"
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
      metric["runtime"] = timer["total_time"] - timer["loading_data"]

    return metric
