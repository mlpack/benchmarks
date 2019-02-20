'''
  @file nbc.py
  @author Marcus Edel
  Class to benchmark the weka Naive Bayes Classifier method.
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
from scipy.io import arff
from functools import reduce
import operator

'''
This class implements the Naive Bayes Classifier benchmark.
'''
class NBC(object):

  '''
  Create the Naive Bayes Classifier benchmark instance.
  @param dataset - Input dataset to perform NBC on.
  @param timeout - The time until the timeout. Default no timeout.
  @param path - Path to the mlpack executable.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, path=os.environ["JAVAPATH"],
      verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.path = path
    self.timeout = timeout
    
  def __del__(self):
    Log.Info("Clean up.", self.verbose)
    filelist = ["weka_predicted.csv"]
    for f in filelist:
      if os.path.isfile(f):
        os.remove(f)

  '''
  Naive Bayes Classifier. If the method has been successfully completed return
  the elapsed time in seconds.
  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform NBC.", self.verbose)

    if len(options) > 0:
      Log.Fatal("Unknown parameters: " + str(options))
      raise Exception("unknown parameters")

    if len(self.dataset) < 2:
      Log.Fatal("This method requires two or more datasets.")
      return -1

    # Split the command using shell-like syntax.
    cmd = shlex.split("java -classpath " + self.path + "/weka.jar" +
        ":methods/weka" + " NBC -t " + self.dataset[0] + " -T " +
        self.dataset[1])

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
      metrics['Runtime'] = timer.total_time
      predictions = np.genfromtxt("weka_predicted.csv", delimiter=',')
      data, meta = arff.loadarff(self.dataset[2])
      truelabels = np.asarray(
        reduce(operator.concat, data.tolist()), dtype=np.float32)
      metrics['Runtime'] = timer.total_time
      try:
        confusionMatrix = Metrics.ConfusionMatrix(truelabels, predictions)
        metrics['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
        metrics['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
        metrics['Precision'] = Metrics.AvgPrecision(confusionMatrix)
        metrics['Recall'] = Metrics.AvgRecall(confusionMatrix)
        metrics['MSE'] = Metrics.SimpleMeanSquaredError(truelabels, predictions)
      except Exception as e:
        # The confusion matrix can't mix binary and continuous data.
        pass

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
    pattern = re.compile(r"""
        .*?total_time: (?P<total_time>.*?)s.*?
        """, re.VERBOSE|re.MULTILINE|re.DOTALL)

    match = pattern.match(data.decode())
    if not match:
      Log.Fatal("Can't parse the data: wrong format")
      return -1
    else:
      # Create a namedtuple and return the timer data.
      timer = collections.namedtuple("timer", ["total_time"])

      if match.group("total_time").count(".") == 1:
        return timer(float(match.group("total_time")))
      else:
        return timer(float(match.group("total_time").replace(",", ".")))
