'''
  @file system.py
  @author Marcus Edel

  Contains functions to get system informations.
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

import platform
import collections
import sys
import shlex
import subprocess

'''
This class implements functions the get system informations.
'''
class SystemInfo(object):

  '''
  Get the available memory of this machine.

  @return The available memory if the plattform is known otherwise 'N/A'.
  '''
  @staticmethod
  def GetMemory():
    if sys.platform.startswith("posix") or sys.platform.startswith("linux"):
      cmd = "free -m"
      s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)

      mem = s.decode().split('\n')[1].split()[1]
      return str(float(mem) / 1024) + ' GB'

    elif sys.platform.startswith('darwin'):
      cmd = shlex.split("sysctl -n hw.memsize")
      mem = subprocess.check_output(cmd, stderr=subprocess.STDOUT, 
          shell=False).strip()

      return str(float(mem) / 1024 / 1024 / 1000.0) + ' GB'

    else:
      return 'N/A'      

  '''
  Get the CPU model name of this machine.

  @return The CPU model of this machine if the plattform otherwise 'N/A'.
  '''
  @staticmethod
  def GetCPUModel():
    if sys.platform.startswith('posix') or sys.platform.startswith('linux'):
      cmd = 'cat /proc/cpuinfo'
      s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, 
          shell=True).strip()
      for line in s.decode().split("\n"):
        if "model name" in line:
          modelName = re.sub( ".*model name.*:", "", line, 1)
          return modelName  
        elif "Processor" in line:
          modelName = re.sub( ".*Processor.*:", "", line, 1)
          return modelName  
      return 'N/A'

    elif sys.platform.startswith('darwin'):
      cmd = shlex.split("sysctl -n machdep.cpu.brand_string")
      modelName = subprocess.check_output(cmd, stderr=subprocess.STDOUT, 
          shell=False).strip()
      return modelName

    elif sys.platform.startswith('win'):
      modelName = platform.processor()
      return modelName

    else:
      Log.Fatal('Could not get the OS name')
      return 'N/A'

  '''
  Get the distribution name of this machine.

  @return The name of the distribution if the plattform is known otherwise 'N/A'.
  '''
  @staticmethod
  def GetDistribution():
    if sys.platform.startswith('posix') or sys.platform.startswith('linux'):
      try:
        osInfo = platform.linux_distribution()
        if len(osInfo) != 0:
          return osInfo[0] + ' ' + osInfo[1]

      except:
        osInfo = platform.dist()
        if len(osInfo) != 0:
          return osInfo[0] + ' ' + osInfo[1]

    elif sys.platform.startswith('darwin'):
      osInfo = platform.mac_ver()
      dist = 'Mac OS X'

      if osInfo[0].startswith('10.6'):
        dist += ' ' + osInfo[0] + ' (Snow Leopard)'
      elif osInfo[0].startswith('10.7'):
        dist += ' ' + osInfo[0] + ' (Lion)'
      elif osInfo[0].startswith('10.8'):
        dist += ' ' + osInfo[0] + ' (Mountain Lion)'
      elif osInfo[0].startswith('10.9'):
        dist += ' ' + osInfo[0] + ' (Mavericks)'

      return dist

    elif sys.platform.startswith('win'):
      pass
    else:
      Log.Fatal('Could not get the OS name')
      return 'N/A'

  '''
  Get the CPU core count of this machine.

  @return The CPU core count if the plattform is known otherwise 'N/A'.
  '''
  @staticmethod
  def GetCPUCores():
    # Python 2.6+ use multiprocessing module.
    try:
      import multiprocessing
      return str(multiprocessing.cpu_count())
    except (ImportError, NotImplementedError):
      pass

    # Python < 2.6.
    if sys.platform.startswith('posix') or sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
      res = int(os.sysconf('SC_NPROCESSORS_ONLN'))

      if res > 0:
        return str(res)

    elif sys.platform.startswith('win'):
      res = int(os.environ['NUMBER_OF_PROCESSORS'])

      if res > 0:
        return res
    else:
      Log.Fatal('Could not specify the OS name')
      return 'N/A'
      
  '''
  Get the plattform of this machine (e.g. x86_64).

  @return The plattform of this machine.
  '''
  @staticmethod
  def GetPlatform():
    return platform.machine()
