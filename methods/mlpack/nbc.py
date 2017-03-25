'''
  @file nbc.py
  @author Marcus Edel

  Class to benchmark the mlpack Parametric Naive Bayes Classifier method.
'''

import os
import sys
import inspect
import numpy as np

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
from misc import *
from definitions import *
import shlex

try:
  import subprocess32 as subprocess
except ImportError:
  import subprocess

import re
import collections

'''
This class implements the Parametric Naive Bayes Classifier benchmark.
'''
class NBC(object):

  '''
  Create the Parametric Naive Bayes Classifier benchmark instance, show some
  informations and return the instance.

  @param dataset - Input dataset to perform Naive Bayes Classifier on.
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
    cmd = shlex.split(self.path + "mlpack_nbc -h")
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
    filelist = ["gmon.out", "output.csv"]
    for f in filelist:
      if os.path.isfile(f):
        os.remove(f)

  '''
  Run valgrind massif profiler on the Parametric Naive Bayes Classifier method.
  If the method has been successfully completed the report is saved in the
  specified file.

  @param options - Extra options for the method.
  @param fileName - The name of the massif output file.
  @param massifOptions - Extra massif options.
  @return Returns False if the method was not successful, if the method was
  successful save the report file in the specified file.
  '''
  def RunMemory(self, options, fileName, massifOptions="--depth=2"):
    Log.Info("Perform NBC Memory Profiling.", self.verbose)

    if len(self.dataset) < 2:
      Log.Fatal("This method requires two datasets.")
      return -1

    # Split the command using shell-like syntax.
    cmd = shlex.split(self.debug + "mlpack_nbc -t " + self.dataset[0] + " -T "
        + self.dataset[1] + " -v " + options)

    return Profiler.MassifMemoryUsage(cmd, fileName, self.timeout, massifOptions)

  '''
  Perform Parametric Naive Bayes Classifier. If the method has been successfully
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform NBC.", self.verbose)

    if len(self.dataset) < 2:
      Log.Fatal("This method requires two datasets.")
      return -1

    # Split the command using shell-like syntax.
    cmd = shlex.split(self.path + "mlpack_nbc -t " + self.dataset[0] + " -T "
        + self.dataset[1] + " -v " + options + " -o output.csv")

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
      metrics['Runtime'] = timer.total_time - timer.saving_data - timer.loading_data
      metrics['Testing'] = timer.nbc_testing
      metrics['Training'] = timer.nbc_testing

      Log.Info(("total time: %fs" % (metrics['Runtime'])), self.verbose)

    if len(self.dataset) >= 3 and CheckFileAvailable('output.csv'):
      testData = LoadDataset(self.dataset[1])
      truelabels = LoadDataset(self.dataset[2])
      predictedlabels = LoadDataset("output.csv")

      confusionMatrix = Metrics.ConfusionMatrix(truelabels, predictedlabels)
      metrics['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
      metrics['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metrics['Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metrics['Recall'] = Metrics.AvgRecall(confusionMatrix)
      metrics['MSE'] = Metrics.SimpleMeanSquaredError(truelabels, predictedlabels)

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
        .*?loading_data: (?P<loading_data>.*?)s.*?
        .*?nbc_testing: (?P<nbc_testing>.*?)s.*?
        .*?nbc_training: (?P<nbc_training>.*?)s.*?
        .*?saving_data: (?P<saving_data>.*?)s.*?
        .*?total_time: (?P<total_time>.*?)s.*?
        """, re.VERBOSE|re.MULTILINE|re.DOTALL)

    match = pattern.match(data)
    if not match:
      Log.Fatal("Can't parse the data: wrong format")
      return -1
    else:
      # Create a namedtuple and return the timer data.
      timer = collections.namedtuple("timer", ["loading_data", "nbc_testing",
          "nbc_training", "saving_data", "total_time"])

      return timer(float(match.group("loading_data")),
                   float(match.group("nbc_testing")),
                   float(match.group("nbc_training")),
                   float(match.group("saving_data")),
                   float(match.group("total_time")))
