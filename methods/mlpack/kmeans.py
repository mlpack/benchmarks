'''
  @file kmeans.py
  @author Marcus Edel

  Class to benchmark the mlpack K-Means clustering method.
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
This class implements the K-Means clustering benchmark.
'''
class MLPACK_KMEANS(object):
  def __init__(self, method_param, run_param):
    # Assemble run command.
    self.dataset = check_dataset(method_param["datasets"], ["csv", "txt"])

    options = ""
    if "clusters" in method_param:
      options += "-c " + str(method_param["clusters"])
    if "max_iterations" in options:
      options += " -m " + str(method_param["max_iterations"])

    if len(self.dataset) == 2:
      self.cmd = shlex.split(run_param["mlpack_path"] + "mlpack_kmeans -i " +
        self.dataset[0] + " -I " + self.dataset[1] + " -o output.csv -v " +
        options)
    else:
      self.cmd = shlex.split(run_param["mlpack_path"] + "mlpack_kmeans -i " +
        self.dataset[0] + " -o output.csv -v " + options)

    self.info = "MLPACK_KMEANS (" + str(self.cmd) + ")"
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
      metric["runtime"] = timer["clustering"]

    return metric
