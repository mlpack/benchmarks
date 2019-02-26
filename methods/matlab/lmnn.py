'''
  @file lmnn.py
  @author Manish Kumar

  Class to benchmark the matlab Large Margin Nearest Neighbors method.
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

import shlex
import subprocess
import re
import collections

'''
This class implements the Large Margin Nearest Neighbors benchmark.
'''
class LMNN(object):

  '''
  Create the Large Margin Nearest Neighbors benchmark instance.

  @param dataset - Input dataset to perform Logistic Regression on.
  @param timeout - The time until the timeout. Default no timeout.
  @param path - Path to the matlab binary.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, path=os.environ["MATLAB_BIN"],
      verbose=True):
    self.verbose = verbose
    self.dataset = dataset
    self.path = path
    self.timeout = timeout
    self.k = 1

  '''
  Destructor to clean up at the end. Use this method to remove created file.
  '''
  def __del__(self):
    Log.Info("Clean up.", self.verbose)
    filelist = ["distance.csv"]
    for f in filelist:
      if os.path.isfile(f):
        os.remove(f)

  '''
  Large Margin Nearest Neighbors benchmark instance. If the method has been
  successfully completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform Large Margin Nearest Neighbors.", self.verbose)

    if "k" in options:
      self.k = int(options.pop("k"))

    # No options accepted for this script.
    if len(options) > 0:
      Log.Fatal("Unknown parameters: " + str(options))
      raise Exception("unknown parameters")

    inputCmd = "-i " + self.dataset + " -k " + str(self.k)

    # Split the command using shell-like syntax.
    cmd = shlex.split(self.path + "matlab -nodisplay -nosplash -r \"try, " +
        "LMNN('"  + inputCmd + "'), catch, exit(1), end, exit(0)\"")

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
      distance = np.genfromtxt("distance.csv", delimiter = ',')
      data = np.genfromtxt(self.dataset, delimiter=',')

      dataList = [data[:,:-1], data[:, (data.shape[1] - 1)]]
      metrics['Accuracy_1_NN'] = Metrics.KNNAccuracy(distance, dataList, 1, False)
      metrics['Accuracy_3_NN'] = Metrics.KNNAccuracy(distance, dataList, 3, False)
      metrics['Accuracy_3_NN_DW'] = Metrics.KNNAccuracy(distance, dataList, 3, True)
      metrics['Accuracy_5_NN'] = Metrics.KNNAccuracy(distance, dataList, 5, False)
      metrics['Accuracy_5_NN_DW'] = Metrics.KNNAccuracy(distance, dataList, 5, True)

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
        .*?total_time: (?P<total_time>.*?)s.*?
        """, re.VERBOSE|re.MULTILINE|re.DOTALL)

    match = pattern.match(data)
    if not match:
      Log.Fatal("Can't parse the data: wrong format")
      return -1
    else:
      # Create a namedtuple and return the timer data.
      timer = collections.namedtuple("timer", ["total_time"])

      return timer(float(match.group("total_time")))

