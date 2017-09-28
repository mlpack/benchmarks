'''
  @file KMEANS.py
  Class to benchmark the dlibml method with KMEANS.
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
import subprocess
import re
import collections

'''
This class implements the KMEANS benchmark.
'''
class KMEANS(object):

  '''
  Create the KMEANS benchmark instance, show some informations
  and return the instance.
  @param dataset - Input dataset to perform KMEANS on.
  @param timeout - The time until the timeout. Default no timeout.
  @param path - Path to the flann executable.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, path=os.environ["DLIBML_PATH"],
        verbose = True):
    self.verbose = verbose
    self.dataset = dataset
    self.path = path
    self.timeout = timeout

  '''
  Destructor to clean up at the end. Use this method to remove created files.
  '''
  def __del__(self):
    Log.Info("Clean up.", self.verbose)
    filelist = ["assignments.csv"]
    for f in filelist:
      if os.path.isfile(f):
        os.remove(f)


  '''
  Perform KMEANS. If the method has been successfully completed
  return the elapsed time in seconds.
  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform KMEANS.", self.verbose)

    # Parse options into string.
    optionsStr = ""
    if "clusters" in options:
      optionsStr = "-k " + str(options.pop("clusters"))
    else:
      Log.Fatal("Required parameter 'clusters' not specified!")
      raise Exception("missing parameter")

    if len(options) > 0:
      Log.Fatal("Unknown parameters: " + str(options))
      raise Exception("unknown parameters")

    # If the dataset contains two files then the second file is the query file.
    # In this case we add this to the command line.
    if len(self.dataset) == 2:
      cmd = shlex.split(self.path + "dlibml_kmeans -r " + self.dataset[0] + " -c " +
          self.dataset[1] + " -v " + optionsStr)
    else:
      cmd = shlex.split(self.path + "dlibml_kmeans -r " + self.dataset +
          " -v " + optionsStr)

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
      metrics['Runtime'] = timer.clustering

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
        .*?clustering: (?P<clustering>.*?)s.*?
        """, re.VERBOSE|re.MULTILINE|re.DOTALL)

    match = pattern.match(data.decode())
    if not match:
      Log.Fatal("Can't parse the data: wrong format")
      return -1
    else:
      # Create a namedtuple and return the timer data.
      timer = collections.namedtuple("timer", ["clustering"])
      return timer(float(match.group("clustering")))
