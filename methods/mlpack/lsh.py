'''
  @file lsh.py
  @author Marcus Edel

  Class to benchmark the mlpack All K-Approximate-Nearest-Neighbor Search with
  LSH method.
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
This class implements the All K-Approximate-Nearest-Neighbor Search benchmark.
'''
class MLPACK_LSH(object):
  def __init__(self, method_param, run_param):
    # Assemble run command.
    self.dataset = check_dataset(method_param["datasets"], ["csv", "txt"])

    options = ""
    if "k" in method_param:
      options += " -k " + str(method_param["k"])
    if "seed" in method_param:
      options += " -s " + str(method_param["seed"])

    self.cmd = shlex.split(run_param["mlpack_path"] + "mlpack_lsh -r " +
      self.dataset[0] + " -v " + options)

    self.info = "MLPACK_LSH (" + str(self.cmd) + ")"
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
      metric["hash_building"] = timer["hash_building"]

    return metric
