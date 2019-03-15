'''
  @file allknn.py
  @author Marcus Edel

  Class to benchmark the weka All K-Nearest-Neighbors method.
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
This class implements the All K-Nearest-Neighbors benchmark.
'''
class WEKA_ALLKNN(object):
  def __init__(self, method_param, run_param):
    # Assemble run command.
    dataset = check_dataset(method_param["datasets"], ["arff"])
    if len(dataset) == 2:
      input_cmd = "-r " + dataset[0] + " -q " + dataset[1] + " "
    else:
      input_cmd = "-r " + dataset[0] + " "

    options = ""
    if "k" in method_param:
      options += "-k " + str(method_param["k"])
    if "seed" in method_param:
      options += " -s " + str(method_param["seed"])

    self.cmd = shlex.split("java -classpath " + run_param["weka_path"] +
      "/weka.jar" + ":methods/weka" + " AllKnn " + input_cmd + " " + options)

    self.info = "WEKA_ALLKNN (" + str(self.cmd) + ")"
    self.timeout = run_param["timeout"]

  def __str__(self):
    return self.info

  def metric(self):
    try:
      output = subprocess.check_output(self.cmd, stderr=subprocess.STDOUT,
        shell=False, timeout=self.timeout)
    except subprocess.TimeoutExpired as e:
      raise Exception("method timeout")
    except Exception as e:
      subprocess_exception(e, self.output)

    metric = {}
    timer = parse_timer(output)
    if timer:
      metric['runtime'] = timer["total_time"]

    return metric
