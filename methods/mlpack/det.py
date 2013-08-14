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
    cmd = shlex.split(self.path + "det -h")
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
  Destructor to clean up at the end. Use this method to remove created files.
  '''
  def __del__(self):
    Log.Info("Clean up.", self.verbose)
    filelist = ["gmon.out", "leaf_class_membership.txt"]
    for f in filelist:
      if os.path.isfile(f):
        os.remove(f)

  '''
  Run valgrind massif profiler on the Principal Components Analysis method. If 
  the method has been successfully completed the report is saved in the 
  specified file.

  @param options - Extra options for the method.
  @param fileName - The name of the massif output file.
  @param massifOptions - Extra massif options.
  @return Returns False if the method was not successful, if the method was 
  successful save the report file in the specified file.
  '''
  def RunMemoryProfiling(self, options, fileName, massifOptions="--depth=2"):
    Log.Info("Perform DET Memory Profiling.", self.verbose)

    # If the dataset contains two files then the second file is the labelsfile.
    # In this case we add this to the command line.
    if len(self.dataset) == 2:
      cmd = shlex.split(self.debug + "det -t " + self.dataset[0] + " -l " + 
          self.dataset[1] + " -v " + options)
    else:
      cmd = shlex.split(self.debug + "det -t " + self.dataset + " -v " + options)

    return Profiler.MassifMemoryUsage(cmd, fileName, self.timeout, massifOptions)

  '''
  Perform Density Estimation With Density Estimation Trees. If the method has 
  been successfully completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def RunMethod(self, options):
    Log.Info("Perform DET.", self.verbose)

    # If the dataset contains two files then the second file is the labelsfile.
    # In this case we add this to the command line.
    if len(self.dataset) == 2:
      cmd = shlex.split(self.path + "det -t " + self.dataset[0] + " -l " + 
          self.dataset[1] + " -v " + options)
    else:
      cmd = shlex.split(self.path + "det -t " + self.dataset + " -v " + options)

    # Run command with the nessecary arguments and return its output as a byte 
    # string. We have untrusted input so we disables all shell based features.
    try:
      s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False, 
          timeout=self.timeout)
    except subprocess.TimeoutExpired as e:
      Log.Warn(str(e))
      return -2
    except Exception as e:
      Log.Fatal("Could not execute command: " + str(cmd))
      return -1

    # Return the elapsed time.
    timer = self.parseTimer(s)
    if not timer:
      Log.Fatal("Can't parse the timer")
      return -1
    else:
      time = self.GetTime(timer)
      Log.Info(("total time: %fs" % (time)), self.verbose)

      return time

  '''
  Parse the timer data form a given string.

  @param data - String to parse timer data from.
  @return - Namedtuple that contains the timer data.
  '''
  def parseTimer(self, data):
    # Compile the regular expression pattern into a regular expression object to
    # parse the timer data.
    pattern = re.compile(br"""
        .*?loading_data: (?P<loading_data>.*?)s.*?
        .*?total_time: (?P<total_time>.*?)s.*?
        """, re.VERBOSE|re.MULTILINE|re.DOTALL)
    
    match = pattern.match(data)
    if not match:
      Log.Fatal("Can't parse the data: wrong format")
      return -1
    else:
      # Create a namedtuple and return the timer data.
      timer = collections.namedtuple("timer", ["loading_data", "total_time"])
      
      return timer(float(match.group("loading_data")), 
          float(match.group("total_time")))

  '''
  Return the elapsed time in seconds.

  @param timer - Namedtuple that contains the timer data.
  @return Elapsed time in seconds.
  '''
  def GetTime(self, timer):
    time = timer.total_time - timer.loading_data
    return time
