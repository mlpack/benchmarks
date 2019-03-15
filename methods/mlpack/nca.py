'''
  @file nca.py
  @author Marcus Edel

  Class to benchmark the mlpack Neighborhood Components Analysis method.
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
This class implements the Neighborhood Components Analysis benchmark.
'''
class MLPACK_NCA(object):
  def __init__(self, method_param, run_param):
    # Assemble run command.
    self.dataset = check_dataset(method_param["datasets"], ["csv", "txt"])

    options = ""
    if "optimizer" in method_param:
      options += " -O " + str(method_param["optimizer"])
    if "max_iterations" in method_param:
      options += " -n " + str(method_param["max_iterations"])
    if "num_basis" in method_param:
      options += " -B " + str(method_param["num_basis"])
    if "wolfe" in method_param:
      options += " -w " + str(method_param["wolfe"])
    if "normalize" in method_param:
      options += " -N"
    if "seed" in method_param:
      options += " --seed " + str(method_param["seed"])

    if len(self.dataset) == 2:
      self.cmd = shlex.split(run_param["mlpack_path"] + "mlpack_nca -i " +
        self.dataset[0] + " -l " + self.dataset[1] + " -v -o distance.csv " +
        options)
    else:
      self.cmd = shlex.split(run_param["mlpack_path"] + "mlpack_nca -i " +
        self.dataset[0] + " -v -o distance.csv " + options)

    self.info = "MLPACK_NCA (" + str(self.cmd) + ")"
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

    return metric
