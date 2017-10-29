'''
  @file logistic_regression.py
  @author Anand Soni

  Class to benchmark the weka Logistic Regression method.
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
This class implements the Logistic Regression benchmark.
'''
class LogisticRegression(object):

  '''
  Create the Logistic Regression benchmark instance.
  @param dataset - Input dataset to perform Logistic Regression on.
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
    filelist = ["weka_predicted.csv", "weka_lr_probabilities.csv"]
    for f in filelist:
      if os.path.isfile(f):
        os.remove(f)

  '''
  Logistic Regression. If the method has been successfully completed return
  the elapsed time in seconds.
  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform Logistic Regression.", self.verbose)

    maxIterStr = ""
    if 'max_iterations' in options:
      maxIterStr = " -m " + str(options['max_iterations']) + " "
      options.pop('max_iterations')

    if len(options) > 0:
      Log.Fatal("Unknown parameters: " + str(options))
      raise Exception("unknown parameters")

    if len(self.dataset) < 2:
      Log.Fatal("This method requires two or more datasets.")
      return -1

    # Split the command using shell-like syntax.
    cmd = shlex.split("java -classpath " + self.path + "/weka.jar" +
        ":methods/weka" + " LogisticRegression -t " + self.dataset[0] + " -T " +
        self.dataset[1] + maxIterStr)

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
      predictions = np.genfromtxt("weka_predicted.csv", delimiter=',')
      truelabels = np.genfromtxt(self.dataset[2], delimiter = ',')
      metrics['Runtime'] = timer.total_time
      confusionMatrix = Metrics.ConfusionMatrix(truelabels, predictions)
      metrics['Avg Accuracy'] = Metrics.AverageAccuracy(confusionMatrix)
      metrics['MultiClass Precision'] = Metrics.AvgPrecision(confusionMatrix)
      metrics['MultiClass Recall'] = Metrics.AvgRecall(confusionMatrix)
      metrics['MultiClass FMeasure'] = Metrics.AvgFMeasure(confusionMatrix)
      metrics['MultiClass Lift'] = Metrics.LiftMultiClass(confusionMatrix)
      metrics['MultiClass MCC'] = Metrics.MCCMultiClass(confusionMatrix)
      metrics['MultiClass Information'] = Metrics.AvgMPIArray(confusionMatrix, truelabels, predictions)
      metrics['Simple MSE'] = Metrics.SimpleMeanSquaredError(truelabels, predictions)

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
