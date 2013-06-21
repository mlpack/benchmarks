'''
  @file lars.py
  @author Marcus Edel

  Class to benchmark the mlpack Least Angle Regression method.
'''

import os
import sys
import inspect

# Import the util path, this method even works if the path contains
# symlinks to modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
	os.path.split(inspect.getfile(inspect.currentframe()))[0], '../../util')))
if cmd_subfolder not in sys.path:
	sys.path.insert(0, cmd_subfolder)

from log import *

import shlex
import subprocess
import re
import collections

class LARS(object):

	# Create the Least Angle Regression instance, show some informations 
	# and return the instance.
	def __init__(self, dataset, path='/usr/local/bin/', verbose=True): 
		self.verbose = verbose
		self.dataset = dataset
		self.path = path

		# Get description from executable.
		cmd = shlex.split(self.path + "lars -h")
		s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False)	

		# Use regular expression pattern to get the description.
		pattern = re.compile(r"""(.*?)Required.*?options:""", 
				re.VERBOSE|re.MULTILINE|re.DOTALL)
		
		match = pattern.match(s)
		if not match:
			Log.Warn("Can't parse description", self.verbose)
			description = ''
		else:
			description = match.group(1)
		
		# Show method informations.
		# Log.Notice(description)
		# Log.Notice('\n')

	# Remove created files.
	def __del__(self):		
		Log.Info('Clean up.', self.verbose)
		filelist = ['gmon.out', 'output.csv']
		for f in filelist:
			if os.path.isfile(f):
				os.remove(f)				

	# Perform Least Angle Regression and return the elapsed time.
	def RunMethod(self, options):
		Log.Info('Perform LARS.', self.verbose)

		if len(self.dataset) < 2:
			Log.Fatal('The method need two datasets.')
			return False

		# Split the command using shell-like syntax.
		cmd = shlex.split(self.path + "lars -i " + self.dataset[0] + " -r " + 
			self.dataset[1] + " -v " + options)

		# Run command with the nessecary arguments and return its output as
		# a byte string. We have untrusted input so we disables all shell 
		# based features.
		s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False)

		print s

		# Return the elapsed time.
		timer = self.parseTimer(s)
		if not timer:
			Log.Fatal("Can't parse the timer", self.verbose)
			return 0
		else:
			time = timer.lars_regression
			Log.Info(('total time: %fs' % (time)), self.verbose)

			return time

	# Parse the timer data.
	def parseTimer(self, data):
		# Compile the regular expression pattern into a regular expression object
		# to parse the timer data.
		pattern = re.compile(r"""
							.*?lars_regression: (?P<lars_regression>.*?)s.*?
							""", re.VERBOSE|re.MULTILINE|re.DOTALL)
		
		match = pattern.match(data)
		if not match:
			print "Can't parse the data: wrong format"
			return False
		else:
			# Create a namedtuple and return the timer data.
			timer = collections.namedtuple('timer', ['lars_regression'])
			if match.group("lars_regression").count(".") == 1:
				return timer(float(match.group("lars_regression")))
			else:
				return timer(float(match.group("lars_regression").replace(",", ".")))	

	# Return the elapsed time.
	def GetTime(self, timer):
		time = timer.total_time - timer.loading_time - timer.saving_time
		return time