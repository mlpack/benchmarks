'''
  @file det.py
  @author Marcus Edel

  Class to benchmark the mlpack Density Estimation With Density Estimation
  Trees method.
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
This class implements the Density Estimation With Density Estimation Trees
benchmark.
'''
class MLPACK_DET(object):
  def __init__(self, method_param, run_param):
    # Assemble run command.
    self.dataset = check_dataset(method_param["datasets"], ["csv", "txt"])

    options = ""
    if "folds" in method_param:
      optionsStr += "-f " + str(method_param["folds"])

    if len(self.dataset) == 2:
      self.cmd = shlex.split(run_param["mlpack_path"] + "mlpack_det -t " +
        self.dataset[0] + " -T " + self.dataset[1] + " -v " + options)
    else:
      self.cmd = shlex.split(run_param["mlpack_path"] + "mlpack_det -t " +
        self.dataset[0] + " -v " + options)

    self.info = "MLPACK_DET (" + str(self.cmd) + ")"
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
      metric["det_training"] = timer["det_training"]

    return metric
