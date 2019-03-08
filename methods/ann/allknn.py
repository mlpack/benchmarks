'''
  @file allknn.py
  @author Marcus Edel

  Class to benchmark the ann All K-Nearest-Neighbors method with kd-trees.
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
This class implements the All K-Nearest-Neighbor Search benchmark.
'''
class ANN_ALLKNN(object):
  def __init__(self, method_param, run_param):
    # Assemble run command.
    self.cmd = run_param["ann_path"] + "allknn"
    if "datasets" in method_param:
      # If the dataset contains two files then the second file is the query
      # file.
      dataset = check_dataset(method_param["datasets"], ["csv", "txt"])
      if len(dataset) == 2:
        self.cmd += " -r " + dataset[0] + " -q " + dataset[1]
      elif len(dataset) == 1:
        self.cmd += " -r " + dataset[0]
    if "k" in method_param:
      self.cmd += " -k " + str(method_param["k"])
    if "seed" in method_param:
      self.cmd += " -s " + str(method_param["seed"])
    if "epsilon" in method_param:
      self.cmd += " -e " + str(method_param["epsilon"])
    self.cmd += " -v"

    self.info = "ANN_ALLKNN (" + self.cmd + ")"
    self.timeout = run_param["timeout"]

  def __str__(self):
    return self.info

  def metric(self):
    try:
      output = subprocess.check_output(self.cmd, stderr=subprocess.STDOUT,
        shell=True, timeout=self.timeout)
    except subprocess.TimeoutExpired as e:
      raise Exception("method timeout")
    except Exception as e:
      raise Exception(str(e))

    metric = {}
    timer = parse_timer(output)
    if timer:
      metric["runtime"] = timer["tree_building"] + timer["computing_neighbors"]
      metric["tree_building"] = timer["tree_building"]
      metric["computing_neighbors"] = timer["computing_neighbors"]

    return metric
