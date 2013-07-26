'''
  @file timer.py
  @author Marcus Edel

  Implementation of the timer class.
'''

from __future__ import with_statement
import time
from functools import wraps
import errno
import os
import signal

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
This Class provides a Timout Error.
'''
class TimeoutError(Exception):
    errno = 23

'''
This function implements a timeout for a function call.

@param seconds - The time until the timeout. Default 5000 seconds.
@param errorMessage - Message for the Error when the timeout is invoked.
@return Timeout error.
'''
def timeout(seconds=5000, errorMessage=os.strerror(errno.ETIME)):
    def decorator(func):
        def handleTimeout(signum, frame):
            raise TimeoutError(errorMessage)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, handleTimeout)
            signal.setitimer(signal.ITIMER_REAL,seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator
