'''
  @file log.py
  @author Marcus Edel

  Implementation of the Log class.
'''

from __future__ import print_function
import re
import sys

'''
This class contains functions to unify the console output.
'''
class Log(object):

  # Color code escape sequences -- but not on Windows.
  if sys.platform == "win32":
    BASH_RED = ""
    BASH_GREEN = ""
    BASH_YELLOW = ""
    BASH_CYAN = ""
    BASH_CLEAR = ""
  else:
    BASH_RED = '\033[0;31m'
    BASH_GREEN = '\033[0;32m'
    BASH_YELLOW = '\033[0;33m'
    BASH_CYAN = '\033[0;36m'
    BASH_CLEAR = '\033[0m'

  '''
  Prints debug output with the appropriate tag: [DEBUG].

  @param line - The line to print to the console.
  @verbose - Display informational messages.
  '''
  @staticmethod
  def Debug(line, verbose=True):
    if verbose:
      print(Log.BASH_CYAN + '[DEBUG] ' + Log.BASH_CLEAR + Log.WrapLine(line), 
          file=sys.stdout)

  '''
  Prints informational messages prefixed with [INFO ].

  @param line - The line to print to the console.
  @verbose - Display informational messages.
  '''
  @staticmethod
  def Info(line, verbose=True):
    if verbose:
      print(Log.BASH_GREEN + '[INFO ] ' + Log.BASH_CLEAR + Log.WrapLine(line), 
          file=sys.stdout)

  '''
  Prints warning messages prefixed with [WARN ].

  @param line - The line to print to the console.
  @verbose - Display informational messages.
  '''
  @staticmethod
  def Warn(line, verbose=True):
    if verbose:
      print(Log.BASH_YELLOW + '[WARN ] ' + Log.BASH_CLEAR + Log.WrapLine(line), 
          file=sys.stdout)

  '''
  Prints fatal messages prefixed with [FATAL].

  @param line - The line to print to the console.
  @verbose - Display informational messages.
  '''
  @staticmethod
  def Fatal(line, verbose=True):
    if verbose:
      print(Log.BASH_RED + '[FATAL] ' + Log.BASH_CLEAR + Log.WrapLine(line), 
          file=sys.stdout)

  '''
  Prints messages without any prefixed.

  @param line - The line to print to the console.
  @verbose - Display informational messages.
  '''
  @staticmethod
  def Notice(line, verbose=True):
    if verbose:
      print(Log.WrapLine(line), file=sys.stdout)

  '''
  Truncate the String into lines of 80 characters.

  @param line - The line to wrap.
  @return The truncated string.
  '''
  @staticmethod
  def WrapLine(line):
    return '\n'.join(line.strip() for line in re.findall(r'.{1,80}(?:\s+|$)', 
        line))

  '''
  Prints out a table of data.

  @param table - A list of a list that contains the table values.
  '''
  @staticmethod
  def PrintTable(table):

    def MaxWidth(table, index):
      return max([len(str(row[index])) for row in table])

    colPaddings = []
    for i in range(len(table[0])):
      colPaddings.append(MaxWidth(table, i))

    for row in table:
      print(row[0].ljust(colPaddings[0] + 1), end=" ", file=sys.stdout)
      for i in range(1, len(row)):
        col = format(row[i]).rjust(colPaddings[i] + 1)
        print(col, end=" ", file=sys.stdout)
      print(file=sys.stdout)
