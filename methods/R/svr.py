'''
  @file svr.py
  Class to benchmark the R SVR method.
'''

import os
import sys
import inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

#Import the metrics definitions path.
metrics_folder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../metrics")))
if metrics_folder not in sys.path:
  sys.path.insert(0, metrics_folder)

from log import *
from profiler import *
from definitions import *
from misc import *

import shlex
import subprocess
import re
import collections
import numpy as np

'''
This class implements the SVR benchmark.
'''
class SVR(object):

  '''
  Create the SVR instance.
  @param dataset - Input dataset to perform SVR on.
  @param timeout - The time until the timeout. Default no timeout.
  @param path - Path to the R executable.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, path=os.environ["R_PATH"],
      verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.path = path
    self.timeout = timeout
    self.build_opts = {}
    
  def __del__(self):
    Log.Info("Clean up.", self.verbose)
    filelist = ["log.txt"]
    for f in filelist:
      if os.path.isfile(f):
        os.remove(f)

  '''
  SVR. If the method has been successfully completed return
  the elapsed time in seconds.
  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform SVR.", self.verbose)

    # Get all the parameters.
    opts = {}
    if "kernel" in options:
      opts["kernel"] = str(options.pop("kernel"))
    else:
      opts["kernel"] = 'radial'

    if "c" in options:
      opts["C"] = float(options.pop("c"))
    else:
      opts["C"] = 1.0
    if "epsilon" in options:
      opts["epsilon"] = float(options.pop("epsilon"))
    else:
      opts["epsilon"] = 1.0
    if "gamma" in options:
      opts["gamma"] = float(options.pop("gamma"))
    else:
      opts["gamma"] = 0.1
    
    if len(options) > 0:
      Log.Fatal("Unknown parameters: " + str(options))
      raise Exception("unknown parameters")

    # Split the command using shell-like syntax.
    cmd = shlex.split("libraries/bin/Rscript " + self.path + "svr.r" +
        " -t " + self.dataset[0] + " -k " + opts['kernel'] + 
	" -c " + str(opts["C"]) + " -e " + str(opts["epsilon"]) + 
	" -g " + str(opts["gamma"]))

    # Run command with the nessecary arguments and return its output as a byte
    # string. We have untrusted input so we disable all shell based features.
    try:
      s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False,
          timeout=self.timeout)
    except subprocess.TimeoutExpired as e:
      Log.Warn(str(e))
      return -2
    except Exception as e:
      Log.Fatal("Could not execute command: " + str(cmd))
      return -1

    # Datastructure to store the results.
    metrics = {}
    # Parse data: runtime.
    timer = self.parseTimer(str(s))
    if timer != -1:
      metrics['Runtime'] = timer

      Log.Info(("total time: %fs" % (metrics['Runtime'])), self.verbose)

    return metrics

  '''
  Parse the timer data form a given string.
  @param data - String to parse timer data from.
  @return - Namedtuple that contains the timer data or -1 in case of an error.
  '''
  def parseTimer(self, data):
    # Compile the regular expression pattern into a regular expression object to
    # parse the timer data.
    pattern = re.findall("(\d+\.\d+). *sec elapsed", data)
    return float(pattern[0])
