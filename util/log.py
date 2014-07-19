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
  Prints the metrics with all related information with the appropriate tag: [METRICS].

  @param line - The line to print to the console.
  @verbose - Display informational messages.
  '''
  @staticmethod
  def Metric(line, verbose=True):
    if verbose:
      print(Log.BASH_GREEN + '[METRICS] ' + Log.BASH_CLEAR + Log.WrapLine(line), 
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

  '''
  Method to print metric dictionary

  @param m_dict - Dictionary containing the metrics for a library
  '''
  @staticmethod
  def print_dict(m_dict):
    print(Log.BASH_GREEN + '[METRICS]' + Log.BASH_CLEAR)
    for key, val in m_dict.items():
      if type(val) is dict:
        print(key, " :\n", Log.print_dict(val))
      else:
        print(key, " : ", val)

  @staticmethod
  def PrintMethodDictionary(method_name, m_dict):
    print("Bootstrapping for method : ", method_name)
    #metric_tabs_dict = {}
    #metric_tabs_count = 1
    header="          "
    for key in m_dict:
      sub_dict = m_dict[key]
      for sub_key in sub_dict:
        if sub_key not in header:
          header += sub_key
          header += "   "
          #metric_tabs_count += 1
          #metric_tabs_dict[sub_key] = metric_tabs_count
    print("   ",header)

    for key in m_dict:
      body = ""
      body += key
      body += "   "
      sub_dictionary = m_dict[key]
      for sub_k in sub_dictionary:
        index = header.rfind(sub_k)
        l = len(sub_k)
        pos = index - len(body)
        pos += l/3
        for i in range(int(pos)):
          body += " "

        body += str(sub_dictionary[sub_k])
      print(body)
    print("Bootstrapping for method ",method_name," done.")
    





    
    
