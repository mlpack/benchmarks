'''
  @file timer.py
  @author Marcus Edel

  Implementation of the timer class.
'''

from __future__ import with_statement
import time

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