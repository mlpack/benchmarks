'''
  @file nmf.py
  @author Marcus Edel

  Class to benchmark the mlpack Non-negative Matrix Factorization method.
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
This class implements the Non-negative Matrix Factorization benchmark.
'''
class MLPACK_NMF(object):
  def __init__(self, method_param, run_param):
    # Assemble run command.
    self.dataset = check_dataset(method_param["datasets"], ["csv", "txt"])

    options = ""
    if "rank" in method_param:
      options += " -r " + str(method_param["rank"])
    if "update_rules" in method_param:
      options += " -u " + str(method_param["update_rules"])
    if "seed" in method_param:
      options += " -s " + str(method_param["seed"])

    self.cmd = shlex.split(run_param["mlpack_path"] + "mlpack_nmf -i " +
      self.dataset[0] + " -H H.csv -W W.csv -v " + options)

    self.info = "MLPACK_NMF (" + str(self.cmd) + ")"
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
