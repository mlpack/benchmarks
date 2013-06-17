'''
  @file pca.py
  @author Marcus Edel

  Class to benchmark the mlpack Principal Components Analysis.
'''

import os
import sys
import inspect

# import the util path, this method even works if the path contains
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


class PCA(object):

	# Create the Principal Components Analysis instance, show some informations 
	# and return the instance.
	def __init__(self, dataset, path='', verbose=True): 
		self.verbose = verbose
		self.dataset = dataset
		self.path = path

		description = '''Principal Components Analysis, or simply PCA is a 
											statistical procedure that uses an orthogonal
											transformation to convert a set of observations
											of possibly correlated variables into a set of values
											of linearly uncorrelated variables called principal 
											components. In particular it allows us to identify 
											the principal directions in which the data varies.
											These statistical procedure has found application 
											in fields such as face recognition and image 
											compression, and is a common technique for finding
											patterns in data of high dimension. In case where a
											graphical representation is not available, PCA is a
											powerful tool for analysing data, without much loss
											of information.'''
		
		# Show method informations.
		#Log.Notice(description)
		#Log.Notice('\n')

	# Remove created files.
	def __del__(self):		
		Log.Info('Clean up.')
		filelist = ['gmon.out', 'output.csv']
		for f in filelist:
			if os.path.isfile(f):
				os.remove(f)				

	# Perform Principal Components Analysis and return the elapsed time.
	def RunMethod(self):
		Log.Info('Perform PCA.', self.verbose)

		# Split the command using shell-like syntax.
		cmd = shlex.split(self.path + "pca -i " + self.dataset + " -o output.csv -v")

		# Run command with the nessecary arguments and return its output as
		# a byte string. We have untrusted input so we disables all shell 
		# based features.
		s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False)		

		# Return the elapsed time.
		timer = self.parseTimer(s)
		if not timer:
			Log.Fatal("can't parse the timer", self.verbose)
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
			print "can't parse the data: wrong format"
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