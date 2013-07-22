'''
  @file hmm_viterbi.py
  @author Marcus Edel

  Class to benchmark the matlab HMM Sequence Log-Likelihood method.
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
This class implements the HMM Sequence Log-Likelihood benchmark.
'''
class HMMVITERBI(object):

  ''' 
  Create the HMM Sequence Log-Likelihood benchmark instance.
  
  @param dataset - Input dataset to perform the HMM Sequence Log-Likelihood on.
  @param path - Path to the matlab binary.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, path=os.environ["MATLAB_BIN"], verbose=True): 
    self.verbose = verbose
    self.dataset = dataset
    self.path = path

  '''
  Destructor to clean up at the end.
  '''
  def __del__(self):
    Log.Info("Clean up.", self.verbose)
    filelist = ["emis_tmp.csv", "trans_tmp.csv"]
    for f in filelist:
      if os.path.isfile(f):
        os.remove(f) 
    
  '''
  HMM Sequence Log-Likelihood. If the method has been successfully completed 
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
  def RunMethod(self, options):
    Log.Info("Perform HMM VITERBI.", self.verbose)

    if len(self.dataset) != 2:
      Log.Fatal("This method requires two datasets.")
      return -1

    # Open the HMM model file and extract the emis and trans values.
    fid = open(self.dataset[1], "r")
    line = fid.read()
    fid.close()

    patternEmis = re.compile(r"""
        .*?<hmm_emission_covariance_.*?>(?P<hmm_emission_mean>.*?)
        </hmm_emission_covariance_
        """, re.VERBOSE|re.MULTILINE|re.DOTALL)

    patternTrans = re.compile(r"""
        .*?<hmm_transition>(?P<hmm_transition>.*?)</hmm_transition>
        """, re.VERBOSE|re.MULTILINE|re.DOTALL)

    emis = patternEmis.findall(line)
    trans = patternTrans.findall(line)

    # Write the emis and trans values to a temporary file.
    if not emis or not trans:
      Log.Fatal("Can't parse the HMM model file.")
      return -1
    else:
      fidEmis = open("emis_tmp.csv", "w")     
      for m in emis:
        m = m.split('\n')
        m = m[0] + "," + m[1] + "\n"
        fidEmis.write(m)

      fidEmis.close()

      fidTrans = open("trans_tmp.csv", "w")
      for m in trans:
        fidTrans.write(m)
      fidTrans.close()

    inputCmd = "-i " + self.dataset[0] + " -e emis_tmp.csv -t trans_tmp.csv " + options
    # Split the command using shell-like syntax.
    cmd = shlex.split(self.path + "matlab -nodisplay -nosplash -r \"try, " +
      "HMM_VITERBI('"  + inputCmd + "'), catch, exit(1), end, exit(0)\"")   
    
    # Run command with the nessecary arguments and return its output as a byte
    # string. We have untrusted input so we disables all shell based features.
    try:
      s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False)   
    except Exception:
      Log.Fatal("Could not execute command: " + str(cmd))
      return -1

    # Return the elapsed time.
    timer = self.parseTimer(s)
    if not timer:
      Log.Fatal("Can't parse the timer")
      return -1
    else:
      time = self.GetTime(timer)
      Log.Info(("total time: %fs" % time), self.verbose)

      return time

  '''
  Parse the timer data form a given string.

  @param data - String to parse timer data from.
  @return - Namedtuple that contains the timer data.
  '''
  def parseTimer(self, data):
    # Compile the regular expression pattern into a regular expression object to
    # parse the timer data.
    pattern = re.compile(r"""
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

  '''
  Return the elapsed time in seconds.

  @param timer - Namedtuple that contains the timer data.
  @return Elapsed time in seconds.
  '''
  def GetTime(self, timer):
    return timer.total_time
