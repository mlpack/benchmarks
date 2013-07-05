'''
  @file local_coordinate_coding.py
  @author Marcus Edel

  Class to benchmark the mlpack Local Coordinate Coding method.
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

import shlex
import subprocess
import re
import collections

'''
This class implements the Local Coordinate Coding benchmark.
'''
class LocalCoordinateCoding(object):

	''' 
	Create the Local Coordinate Coding benchmark instance, show some informations 
	and return the instance.
  
  @param dataset - Input dataset to perform PCA on.
  @param path - Path to the mlpack executable.
  @param verbose - Display informational messages.
	'''
	def __init__(self, dataset, path=os.environ["MLPACK_BIN"], verbose=True): 
		self.verbose = verbose
		self.dataset = dataset
		self.path = path

		# Get description from executable.
		cmd = shlex.split(self.path + "local_coordinate_coding -h")
		try:
			s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False)	
		except Exception, e:
			Log.Fatal("Could not execute command: " + str(cmd))
			return -1

		# Use regular expression pattern to get the description.
		pattern = re.compile(r"""(.*?)Required.*?options:""", 
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
		filelist = ["gmon.out", "codes.csv", "dictionary.csv"]
		for f in filelist:
			if os.path.isfile(f):
				os.remove(f)				

	'''
  Perform Local Coordinate Coding. If the method the has been successfully 
  completed return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
	def RunMethod(self, options):
		Log.Info("Perform Local Coordinate Coding.", self.verbose)

		cmd = shlex.split(self.path + "local_coordinate_coding -i " + self.dataset +
				" -v " + options)

		# Run command with the nessecary arguments and return its output as a byte 
		# string. We have untrusted input so we disables all shell based features.
		try:
			s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False)	
		except Exception, e:
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
		pattern = re.compile(r"""
				.*?loading_data: (?P<loading_data>.*?)s.*?
				.*?saving_data: (?P<saving_data>.*?)s.*?
				.*?total_time: (?P<total_time>.*?)s.*?
				""", re.VERBOSE|re.MULTILINE|re.DOTALL)
		
		match = pattern.match(data)
		if not match:
			Log.Fatal("Can't parse the data: wrong format")
			return -1
		else:
			# Create a namedtuple and return the timer data.
			timer = collections.namedtuple("timer", ["loading_data", "saving_data", 
					"total_time"])
			
			return timer(float(match.group("loading_data")),
					float(match.group("saving_data")),
					float(match.group("total_time")))

	'''
	Return the elapsed time in seconds.

	@param timer - Namedtuple that contains the timer data.
	@return Elapsed time in seconds.
	'''
	def GetTime(self, timer):
		time = timer.total_time - timer.loading_data
		return time
