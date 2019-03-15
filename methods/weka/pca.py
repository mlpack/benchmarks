'''
  @file pca.py
  @author Marcus Edel

  Class to benchmark the weka Principal Components Analysis method.
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
This class implements the Principal Components Analysis benchmark.
'''
class WEKA_PCA(object):
  def __init__(self, method_param, run_param):
    # Assemble run command.
    dataset = check_dataset(method_param["datasets"], ["arff"])

    print(dataset)

    options_str = ""
    if "new_dimensionality" in method_param:
      options_str += "-d " + str(method_param["new_dimensionality"])
    if "whiten" in method_param:
      options_str += " -s"

    self.cmd = shlex.split("java -classpath " + run_param["weka_path"] +
      "weka.jar" + ":methods/weka" + " PCA -i " + dataset[0] + " " +
      options_str)

    self.info = "WEKA_PCA (" + str(self.cmd) + ")"
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
      metric['runtime'] = timer["total_time"]

    return metric
