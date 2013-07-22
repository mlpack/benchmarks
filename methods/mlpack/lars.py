'''
  @file lars.py
  @author Marcus Edel

  Class to benchmark the mlpack Least Angle Regression method.
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
This class implements the Least Angle Regression benchmark.
'''
class LARS(object):

	''' 
	Create the Least Angle Regression benchmark instance, show some informations 
	and return the instance.
  
  @param dataset - Input dataset to perform Least Angle Regression on.
  @param path - Path to the mlpack executable.
  @param verbose - Display informational messages.
	'''
	def __init__(self, dataset, path=os.environ["MLPACK_BIN"], verbose=True): 
		self.verbose = verbose
		self.dataset = dataset
		self.path = path

		# Get description from executable.
		cmd = shlex.split(self.path + "lars -h")
		try:
			s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False)	
		except Exception, e:
			Log.Fatal("Could not execute command: " + str(cmd))
		else:
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
		filelist = ["gmon.out", "output.csv"]
		for f in filelist:
			if os.path.isfile(f):
				os.remove(f)				

	'''
  Perform  Least Angle Regression. If the method has been successfully completed
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or -1 if the method was not successful.
  '''
	def RunMethod(self, options):
		Log.Info("Perform LARS.", self.verbose)

		if len(self.dataset) < 2:
			Log.Fatal("This method requires two datasets.")
			return -1

		# Split the command using shell-like syntax.
		cmd = shlex.split(self.path + "lars -i " + self.dataset[0] + " -r " + 
				self.dataset[1] + " -v " + options)

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
			time = timer.lars_regression
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
				.*?lars_regression: (?P<lars_regression>.*?)s.*?
				""", re.VERBOSE|re.MULTILINE|re.DOTALL)
		
		match = pattern.match(data)
		if not match:
			Log.Fatal("Can't parse the data: wrong format")
			return -1
		else:
			# Create a namedtuple and return the timer data.
			timer = collections.namedtuple("timer", ["lars_regression"])
			
			return timer(float(match.group("lars_regression")))	
