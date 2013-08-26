'''
  @file timer.py
  @author Marcus Edel

  Implementation of the timer class.
'''

from __future__ import with_statement
import os
import sys
import inspect

# Import the util path, this method even works if the path contains symlinks to 
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from log import *

import time
from multiprocessing import Process, Queue

'''
This class implements three functions to measure the time.
'''
class Timer(object):
  '''
  Start the timer.
  '''
  def __enter__(self):
    self.__start = time.time()

  '''
  Stop the timer.
  '''
  def __exit__(self, type, value, traceback):
    self.__finish = time.time()
  
  '''
  Return the elapsed time of the timer.
  '''
  def ElapsedTime(self):
    return self.__finish - self.__start

'''
This function implements a timeout for a function call.

@param fun - Start the process with the given function.
@param timeout - The time until the timeout. Default 9000 seconds.
@return The return value of the process.
'''
def timeout(fun, timeout=9000):
  q = Queue()
  p = Process(target=fun, args=(q,))
  p.start()
  p.join(timeout)

  if p.is_alive():
    # Terminate the process.
    p.terminate()
    p.join()

    Log.Warn("Script timed out after " + str(timeout) + " seconds")
    return -2
  else:
    return q.get()
