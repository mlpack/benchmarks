'''
  @file mlp_backward.py
  @author Marcus Edel

  Class to benchmark the mlpack mlp backward pass.
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

from log import *
from profiler import *

import shlex

try:
  import subprocess32 as subprocess
except ImportError:
  import subprocess

import re
import collections

'''
This class implements the MLP backward benchmark.
'''
class MLP_BACKWARD(object):

  '''
  Create the mlp backward benchmark instance, show some informations and
  return the instance.

  @param dataset - Input dataset to perform the benchmark on.
  @param timeout - The time until the timeout. Default no timeout.
  @param path - Path to the mlpack executable.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, path=os.environ["MLPACK_BIN_SRC"],
      verbose=True, debug=os.environ["MLPACK_BIN_DEBUG_SRC"]):
    self.verbose = verbose
    self.dataset = dataset
    self.path = path
    self.timeout = timeout
    self.debug = debug

    # Get description from executable.
    cmd = shlex.split(self.path + "mlp_backward -h")
    try:
      s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False)
    except Exception as e:
      Log.Fatal("Could not execute command: " + str(cmd))
    else:
      # Use regular expression pattern to get the description.
      pattern = re.compile(br"""(.*?)Required.*?options:""",
          re.VERBOSE|re.MULTILINE|re.DOTALL)

      match = pattern.match(s)
      if not match:
        Log.Warn("Can't parse description", self.verbose)
        description = ""
      else:
        description = match.group(1)

      self.description = description

  '''
  Given an input dict of options, convert it to an output string that can be
  used by the program.
  '''
  def OptionsToStr(self, options):
    optionsStr = ""
    if "input_size" in options:
      optionsStr = "--input_size " + str(options.pop("input_size"))
    if "hidden_size" in options:
      optionsStr = optionsStr + " --hidden_size " +
          str(options.pop("hidden_size"))
    if "output_size" in options:
      optionsStr = optionsStr + " --output_size " +
          str(options.pop("output_size"))

    if len(options) > 0:
      Log.Fatal("Unknown parameters:" + str(options))
      raise Exception("unknown parameters")

    return optionsStr

  '''
  Perform the linear backward pass. If the method has been successfully
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform MLP Backward.", self.verbose)

    # Split the command using shell-like syntax.
    cmd = shlex.split(self.path + "mlp_backward -v " +
        self.OptionsToStr(options))

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
    timer = self.parseTimer(s)

    if timer != -1:
      metrics['Runtime'] = timer.backward - timer.forward
      metrics['Backward'] = timer.backward - timer.forward
      metrics['ModelBuilding'] = timer.model_building

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
    pattern = re.compile(br"""
        .*?backward: (?P<backward>.*?)s.*?
        .*?forward: (?P<forward>.*?)s.*?
        .*?model_building: (?P<model_building>.*?)s.*?
        .*?total_time: (?P<total_time>.*?)s.*?
        """, re.VERBOSE|re.MULTILINE|re.DOTALL)

    match = pattern.match(data)
    if not match:
      Log.Fatal("Can't parse the data: wrong format")
      return -1
    else:
      # Create a namedtuple and return the timer data.
      timer = collections.namedtuple("timer", ["backward", "forward",
          "model_building", "total_time"])

      return timer(float(match.group("backward")),
                   float(match.group("forward")),
                   float(match.group("model_building")),
                   float(match.group("total_time")))
