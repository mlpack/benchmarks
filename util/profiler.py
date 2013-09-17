'''
  @file profiler.py
  @author Marcus Edel

  Contains functions to get profiling informations.
'''

import os
import sys
import inspect

# import the util path, this method even works if the path contains
# symlinks to modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], '')))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from log import *

'''
This class implements functions the get profiling informations.
'''
class Profiler(object):

  '''
  Use valgrind massif to get memory profiling information and save the ouput in 
  the specified file.

  @param command - Method command line to profile.
  @param output - Save the report at the output path with the specified name.
  @param options - Specified massif options.
  @param valgrind - Path to the valgrind binary.
  @ return Returns -1 if the method was not successful, if the method was 
  successful save the report file in the specified file. 
  '''
  @staticmethod
  def MassifMemoryUsage(command, output, timeout, options, 
      valgrind=os.environ["VALGRIND_BIN"]):
    import shlex, subprocess

    cmd = shlex.split(("%s --tool=massif --massif-out-file=%s %s ") % 
        (valgrind, output, options)) + command
    try:
      s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False, 
          timeout=timeout)
    except Exception:
      Log.Fatal("Could not execute command: " + str(cmd))
      return -1

  '''
  Use the valgrind ms_print script to generate the massif output.

  @param fileName - The filname of the valgrind massif log file.
  @param valgrind - The path to the ms_print script.
  @return The ms_print output if the method was successful otherwise -1.
  '''
  @staticmethod
  def MassifMemoryUsageReport(fileName, valgrind=os.environ["MS_PRINT_BIN"]):
    import shlex, subprocess

    cmd = shlex.split(valgrind + " " + fileName)
    try:
      s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False)
      return s
    except Exception:
      Log.Fatal("Could not execute command: " + str(cmd))
      return -1

  '''
  Returns the memory used by a process and his children. We don't know when the 
  process is done so we have to poll to get the memory. To avoid memory overflow
  we use a ringbuffer to limit the size of the memory values.

  @param process - Popen instance.
  @param Buffersize - Memory value count.
  @return List of memory values.
  '''
  @staticmethod
  def SubprocessMemoryUsage(process, Buffersize=200):
    import psutil, time, collections

    # Create the process list with the main process and his childrens.
    p = psutil.Process(process.pid)
    children = list(p.get_children(recursive=True)) + [p]

    memoryTable = collections.deque(maxlen=Buffersize)

    # We have to poll to get the memory values.
    while process.poll() == None:
      try:
        for p in children:
          memoryTable.append(int(p.get_memory_info()[0]))
      # Sometimes a subprocess has terminated in the time between we measure the
      # memory. In this case, we continue.
      except psutil.NoSuchProcess: 
        continue        
      except psutil.AccessDenied: 
        continue

      time.sleep(0.01)

    return memoryTable
