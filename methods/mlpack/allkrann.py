'''
  @file allkrann.py
  @author Marcus Edel

  Class to benchmark the mlpack All K-Rank-Approximate-Nearest-Neighbors method.
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
This class implements the All K-Rank-Approximate-Nearest-Neighbors benchmark.
'''
class ALLKRANN(object):

  '''
  Create the All K-Rank-Approximate-Nearest-Neighbors benchmark instance, show
  some informations and return the instance.

  @param dataset - Input dataset to perform ALLKRANN on.
  @param timeout - The time until the timeout. Default no timeout.
  @param path - Path to the mlpack executable.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, path=os.environ["BINPATH"],
      verbose=True, debug=os.environ["DEBUGBINPATH"]):
    self.verbose = verbose
    self.dataset = dataset
    self.path = path
    self.timeout = timeout
    self.debug = debug

    # Get description from executable.
    cmd = shlex.split(self.path + "mlpack_allkrann -h")
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
    filelist = ["gmon.out", "distances.csv", "neighbors.csv"]
    for f in filelist:
      if os.path.isfile(f):
        os.remove(f)

  '''
  Convert options dict to string usable by programs.
  '''
  def OptionsToStr(self, options):
    optionsStr = ""
    if "k" in options:
      optionsStr = "-k " + str(options.pop("k"))
    else:
      Log.Fatal("Required parameter 'k' not specified!")
      raise Exception("missing parameter")

    if "tau" in options:
      optionsStr = optionsStr + " -T " + str(options.pop("tau"))
    if "naive_mode" in options:
      optionsStr = optionsStr + " --naive"
      options.pop("naive_mode")
    if "single_mode" in options:
      optionsStr = optionsStr + " --single_mode"
      options.pop("single_mode")
    if "sample_at_leaves" in options:
      optionsStr = optionsStr + " -L"
      options.pop("sample_at_leaves")
    if "first_leaf_exact" in options:
      optionsStr = optionsStr + " -X"
      options.pop("first_leaf_exact")

    if len(options) > 0:
      Log.Fatal("Unknown parameters: " + str(options))
      raise Exception("unknown parameters")

    return optionsStr

  '''
  Run valgrind massif profiler on the All K-Rank-Approximate-Nearest-Neighbors
  method. If the method has been successfully completed the report is saved in
  the specified file.

  @param options - Extra options for the method.
  @param fileName - The name of the massif output file.
  @param massifOptions - Extra massif options.
  @return Returns False if the method was not successful, if the method was
  successful save the report file in the specified file.
  '''
  def RunMemory(self, options, fileName, massifOptions="--depth=2"):
    Log.Info("Perform ALLKRANN Memory Profiling.", self.verbose)

    # If the dataset contains two files then the second file is the query file.
    # In this case we add this to the command line.
    if len(self.dataset) == 2:
      cmd = shlex.split(self.debug + "mlpack_allkrann -r " + self.dataset[0] +
          " -q " + self.dataset[1] + " -v -n neighbors.csv -d distances.csv " +
          self.OptionsToStr(options))
    else:
      cmd = shlex.split(self.debug + "mlpack_allkrann -r " + self.dataset +
          " -v -n neighbors.csv -d distances.csv " + self.OptionsToStr(options))

    return Profiler.MassifMemoryUsage(cmd, fileName, self.timeout, massifOptions)

  '''
  Run all the metrics.

  @param options - Extra options for the method.
  @return - dictionary with metrics values or None if the method was
  not successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform ALLKRANN.", self.verbose)

    # If the dataset contains two files then the second file is the query file.
    # In this case we add this to the command line.
    if len(self.dataset) == 2:
      cmd = shlex.split(self.path + "mlpack_allkrann -r " + self.dataset[0] +
          " -q " + self.dataset[1] + " -v -n neighbors.csv -d distances.csv " +
          self.OptionsToStr(options))
    else:
      cmd = shlex.split(self.path + "mlpack_allkrann -r " + self.dataset +
          " -v -n neighbors.csv -d distances.csv " + self.OptionsToStr(options))

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

    # Parse data runtime.
    timer = self.parseTimer(s)

    if timer != -1:
      metrics['Runtime'] = timer.total_time - timer.loading_data - timer.saving_data
      metrics['TreeBuilding'] = timer.tree_building
      metrics['ComputingNeighbors'] = timer.computing_neighbors

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
              .*?computing_neighbors: (?P<computing_neighbors>.*?)s.*?
              .*?loading_data: (?P<loading_data>.*?)s.*?
              .*?saving_data: (?P<saving_data>.*?)s.*?
              .*?total_time: (?P<total_time>.*?)s.*?
              .*?tree_building: (?P<tree_building>.*?)s.*?
              """, re.VERBOSE|re.MULTILINE|re.DOTALL)

    match = pattern.match(data)

    if not match:
      Log.Fatal("Can't parse the data: wrong format")
      return -1
    else:
      # Create a namedtuple and return the timer data.
      timer = collections.namedtuple("timer", ["computing_neighbors",
          "loading_data", "saving_data", "total_time", "tree_building"])

      return timer(float(match.group("computing_neighbors")),
                   float(match.group("loading_data")),
                   float(match.group("saving_data")),
                   float(match.group("total_time")),
                   float(match.group("tree_building")))
