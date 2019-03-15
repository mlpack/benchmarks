'''
  @file allkrann.py
  @author Marcus Edel

  Class to benchmark the mlpack All K-Rank-Approximate-Nearest-Neighbors method.
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
This class implements the All K-Rank-Approximate-Nearest-Neighbors benchmark.
'''
class MLPACK_ALLKRANN(object):
  def __init__(self, method_param, run_param):
    # Assemble run command.
    self.dataset = check_dataset(method_param["datasets"], ["csv", "txt"])

    options = ""
    if "k" in method_param:
      options += "-k " + str(method_param["k"])
    if "tau" in method_param:
      options += " -T " + str(method_param["tau"])
    if "naive_mode" in method_param:
      options += " --naive"
    if "single_mode" in method_param:
      options += " --single_mode"
    if "sample_at_leaves" in method_param:
      options += " -L"
    if "first_leaf_exact" in method_param:
      options += " -X"

    if len(self.dataset) == 2:
      self.cmd = shlex.split(run_param["mlpack_path"] + "mlpack_krann -r " +
        self.dataset[0] + " -q " + self.dataset[1] +
        " -v -n neighbors.csv -d distances.csv " + options)
    else:
      self.cmd = shlex.split(run_param["mlpack_path"] + "mlpack_krann -r " +
        self.dataset[0] + " -v -n neighbors.csv -d distances.csv " + options)

    self.info = "MLPACK_ALLKRANN (" + str(self.cmd) + ")"
    self.timeout = run_param["timeout"]
    self.output = None

  def __str__(self):
    return self.info

  def parse_num_base_cases(self, data):
    pattern = re.compile(
        br""".*[^\d](?P<num_base_cases>\d+) base cases were calculated.*""",
        re.MULTILINE|re.DOTALL)

    match = pattern.match(data)
    if not match:
      return None

    return int(match.group("num_base_cases"))

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
      metric["tree_building"] = timer["tree_building"]
      metric["computing_neighbors"] = timer["computing_neighbors"]

    base_cases = self.parse_num_base_cases(self.output)
    if base_cases:
      metric["base_cases"] = base_cases

    return metric
