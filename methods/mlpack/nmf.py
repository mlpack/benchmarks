'''
  @file nmf.py
  @author Marcus Edel

  Class to benchmark the mlpack Non-negative Matrix Factorization method.
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

class NMF(object):

	# Create the Non-negative Matrix Factorization instance, show some informations 
	# and return the instance.
	def __init__(self, dataset, path='/usr/local/bin/', verbose=True): 
		self.verbose = verbose
		self.dataset = dataset
		self.path = path

		# Get description from executable.
		cmd = shlex.split(self.path + "nmf -h")
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
		filelist = ['gmon.out', 'W.csv', 'H.csv']
		for f in filelist:
			if os.path.isfile(f):
				os.remove(f)				

	# Perform Non-negative Matrix Factorization and return the elapsed time.
	def RunMethod(self, options):
		Log.Info('Perform NMF.', self.verbose)

		# Split the command using shell-like syntax.
		cmd = shlex.split(self.path + "nmf -i " + self.dataset + " -H H.csv -W W.csv -v " + options)

		# Run command with the nessecary arguments and return its output as
		# a byte string. We have untrusted input so we disables all shell 
		# based features.
		s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False)

		# Return the elapsed time.
		timer = self.parseTimer(s)
		if not timer:
			Log.Fatal("Can't parse the timer", self.verbose)
			return 0
		else:
			time = self.GetTime(timer)
			Log.Info(('total time: %fs' % (time)), self.verbose)

			return time

	# Parse the timer data.
	def parseTimer(self, data):
		# Compile the regular expression pattern into a regular expression object
		# to parse the timer data.
		pattern = re.compile(r"""
							.*?loading_data: (?P<loading_time>.*?)s.*?
							.*?saving_data: (?P<saving_time>.*?)s.*?
							.*?total_time: (?P<total_time>.*?)s.*?
							""", re.VERBOSE|re.MULTILINE|re.DOTALL)
		
		match = pattern.match(data)
		if not match:
			print "Can't parse the data: wrong format"
			return False
		else:
			# Create a namedtuple and return the timer data.
			timer = collections.namedtuple('timer', ['loading_time', 
					'saving_time', 'total_time'])
			if match.group("loading_time").count(".") == 1:
				return timer(float(match.group("loading_time")),
						 	float(match.group("saving_time")),
						 	float(match.group("total_time")))
			else:
				return timer(float(match.group("loading_time").replace(",", ".")),
						 	float(match.group("saving_time").replace(",", ".")),
						 	float(match.group("total_time").replace(",", ".")))	

	# Return the elapsed time.
	def GetTime(self, timer):
		time = timer.total_time - timer.loading_time - timer.saving_time
		return time