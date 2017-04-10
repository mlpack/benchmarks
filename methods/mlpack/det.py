'''
  @file det.py
  @author Marcus Edel

  Class to benchmark the mlpack Density Estimation With Density Estimation
  Trees method.
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
This class implements the Density Estimation With Density Estimation Trees
benchmark.
'''
class DET(object):

  '''
  Create the Estimation With Density Estimation Trees benchmark instance, show
  some informations and return the instance.

  @param dataset - Input dataset to perform Density Estimation on.
  @param timeout - The time until the timeout. Default no timeout.
  @param path - Path to the mlpack executable.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, path=os.environ["MLPACK_BIN"],
      verbose=True, debug=os.environ["MLPACK_BIN_DEBUG"]):
    self.verbose = verbose
    self.dataset = dataset
    self.path = path
    self.timeout = timeout
    self.debug = debug

    # Get description from executable.
    cmd = shlex.split(self.path + "mlpack_det -h")
    try:
      s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False)
    except Exception as e:
      Log.Fatal("Could not execute command: " + str(cmd))
    else:
      # Use regular expression pattern to get the description.
      pattern = re.compile(br"""(.*?)Optional.*?options:""",
          re.VERBOSE|re.MULTILINE|re.DOTALL)

      match = pattern.match(s)
      if not match:
        Log.Warn("Can't parse description", self.verbose)
        description = ""
      else:
        description = match.group(1)

      self.description = description

  '''
  Destructor to clean up at the end. Use this method to remove created files.
  '''
  def __del__(self):
    Log.Info("Clean up.", self.verbose)
    filelist = ["gmon.out", "leaf_class_membership.txt"]
    for f in filelist:
      if os.path.isfile(f):
        os.remove(f)

  '''
  Run valgrind massif profiler on the Density Estimation method. If the method
  has been successfully completed the report is saved in the specified file.

  @param options - Extra options for the method.
  @param fileName - The name of the massif output file.
  @param massifOptions - Extra massif options.
  @return Returns False if the method was not successful, if the method was
  successful save the report file in the specified file.
  '''
  def RunMemory(self, options, fileName, massifOptions="--depth=2"):
    Log.Info("Perform DET Memory Profiling.", self.verbose)

    # If the dataset contains two files then the second file is the test file.
    # In this case we add this to the command line.
    if len(self.dataset) == 2:
      cmd = shlex.split(self.debug + "mlpack_det -t " + self.dataset[0] +
          " -T " + self.dataset[1] + " -v " + options)
    else:
      cmd = shlex.split(self.debug + "mlpack_det -t " + self.dataset + " -v " +
          options)

    return Profiler.MassifMemoryUsage(cmd, fileName, self.timeout, massifOptions)

  '''
  Perform Density Estimation With Density Estimation Trees. If the method has
  been successfully completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform DET.", self.verbose)

    # If the dataset contains two files then the second file is the test file.
    # In this case we add this to the command line.
    if len(self.dataset) == 2:
      cmd = shlex.split(self.path + "mlpack_det -t " + self.dataset[0] +
          " -T " + self.dataset[1] + " -v " + options)
    else:
      cmd = shlex.split(self.path + "mlpack_det -t " + self.dataset + " -v " +
          options)

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

    # Parse data: runtime, test time.
    testTime = self.parseTestingTime(s)
    timer = self.parseTimer(s)

    if timer != -1:
      metrics['Runtime'] = timer.total_time - timer.loading_data
      metrics['Training'] = timer.det_training

      Log.Info(("total time: %fs" % (metrics['Runtime'])), self.verbose)

    if testTime != -1:
      metrics['Testing'] = testTime

    return metrics

  '''
  Parse the time need to test.

  @param data - String to parse information from.
  @return - float time to performe testing.
  '''
  def parseTestingTime(self, data):
    # Compile the regular expression pattern into a regular expression object to
    # parse the verbose output.
    pattern = re.compile(br"""
              .*?det_test_set_estimation: (?P<det_test_set_estimation>.*?)s.*?
              """, re.VERBOSE|re.MULTILINE|re.DOTALL)

    match = pattern.match(data)

    if not match:
      # Can't parse the base cases: wrong format
      return -1
    else:
      return float(match.group("det_test_set_estimation"))

  '''
  Parse the timer data from a given string.

  @param data - String to parse timer data from.
  @return - Namedtuple that contains the timer data or -1 in case of an error.
  '''
  def parseTimer(self, data):
    # Compile the regular expression pattern into a regular expression object to
    # parse the timer data.
    pattern = re.compile(br"""
              .*?det_training: (?P<det_training>.*?)s.*?
              .*?loading_data: (?P<loading_data>.*?)s.*?
              .*?total_time: (?P<total_time>.*?)s.*?
              """, re.VERBOSE|re.MULTILINE|re.DOTALL)

    match = pattern.match(data)

    if not match:
      Log.Fatal("Can't parse the data: wrong format")
      return -1
    else:
      # Create a namedtuple and return the timer data.
      timer = collections.namedtuple("timer", ["det_training",
          "loading_data", "total_time"])

      return timer(float(match.group("det_training")),
                   float(match.group("loading_data")),
                   float(match.group("total_time")))
