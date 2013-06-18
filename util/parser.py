'''
  @file parser.py
  @author Marcus Edel

  Class to parse and check config file.
'''

import os
import sys
import inspect

# Import the util path, this method even works if the path contains
# symlinks to modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
	os.path.split(inspect.getfile(inspect.currentframe()))[0], 'util')))
if cmd_subfolder not in sys.path:
	sys.path.insert(0, cmd_subfolder)

from log import *

import yaml
import collections

class Parser(object):

	# Create the parser instance and load the config file.
	def __init__(self, config, verbose=True):
		self.verbose = verbose
		self.config = config

		# Default values.
		self.RUN = True
		self.ITERATION = 2
		self.PLOT = []

		try:
			Log.Info('Load config file: ' + config, verbose)
			streams = yaml.load_all(open(config))
			self.streams = streams

		except IOError, e:
			Log.Fatal('Could not load config file: ' + config)
		except yaml.YAMLError, exc:
			if hasattr(exc, 'problem_mark'):
				mark = exc.problem_mark
				Log.Fatal('Error at position: (%s:%s)' % (mark.line+1, mark.column+1))

	# Return the library name and a methods instance.
	def GetConfigLibraryMethods(self):
		try:
			stream = self.streams.next()
		except StopIteration, e:
			# We have to catch the exception to stop at the end.
			# There exists no hasNext().
			return False

		if not stream.has_key('library'):
				return self.ConfigKeyErrorMsg('library', streamNum)
		else:
			libraryName = stream['library']
			Log.Info('Library: ' + libraryName, self.verbose)

		attr = collections.namedtuple('attributes', ['libraryName', 'methods'])
			
		return attr(libraryName, stream['methods'].iteritems())


	# Return the method attributes.
	def GetConfigMethod(self, methods):
		try:
			method = methods.next()		
		except StopIteration, e:
			# We have to catch the exception to stop at the end.
			# There exists no hasNext().
			return False

		methodName = method[0]
		Log.Info('Method: ' + methodName)

		attributes = method[1]

		# First check the required attributes. 
		if attributes.has_key('script'):
			script = attributes['script']
			Log.Info('Script: ' + script, self.verbose)
		else:
			return self.ConfigKeyErrorMsg('script')

		if attributes.has_key('format'):
			format = attributes['format']
			Log.Info('Format: ' + str(format), self.verbose)
		else:
			return self.ConfigKeyErrorMsg('format')

		if attributes.has_key('dataset'):
			dataset = attributes['dataset']
			Log.Info('Dataset: ' + str(dataset), self.verbose)
		else:
			return self.ConfigKeyErrorMsg('dataset')

		# Check the optional attributes. 
		if attributes.has_key('run'):
			run = attributes['run']
			Log.Info('Run: ' + str(run), self.verbose)
		else:
			self.ConfigKeyWarnMsg('run')
			run = self.RUN

		if attributes.has_key('iteration'):
			iteration = attributes['iteration']
			Log.Info('Iteration: ' + str(iteration), self.verbose)
		else:
			self.ConfigKeyWarnMsg('iteration')
			iteration = self.ITERATION

		if attributes.has_key('plot'):
			plot = attributes['plot']
			Log.Info('plot: ' + str(plot), self.verbose)
		else:
			self.ConfigKeyWarnMsg('plot')
			plot = self.PLOT

		attr = collections.namedtuple('attributes', ['methodName', 'script', 
				'format', 'dataset', 'run', 'iteration', 'plot'])

		return attr(methodName, script, format, dataset, run, iteration, plot)

	# Return key error message.
	def ConfigKeyErrorMsg(self, key, streamNum = 0):
		if streamNum == 0:
			Log.Fatal('No [' + key + '] key.')
		else:
			Log.Fatal('Stream number: ' + str(streamNum) + ' has no [' + key + '] key.')
		
		return False

	# Return empty list error message.
	def ConfigEmptyErrorMsg(self, key, streamNum):
		Log.Fatal('Stream number: ' + str(streamNum) + ' the [' + key +  '] list is empty.' )
		return False

	def ConfigKeyWarnMsg(self, key, streamNum = 0):
		if streamNum == 0:
			Log.Warn('No [' + key + '] key, use default value.')
		else:	
			Log.Warn('Stream number: ' + str(streamNum) + ' has no [' + key + '] key, use default value.')
	
	# Check config attributes and keys.	
	def CheckConfig(self):
		Log.Info('Check config file: ' + self.config, self.verbose)
		streamNum = 0
		for stream in self.streams:
			streamNum += 1

			if not stream.has_key('library'):
				return self.ConfigKeyErrorMsg('library', streamNum)
			elif not stream.has_key('methods'):
				return self.ConfigKeyErrorMsg('methods', streamNum)
			else:
				try:
					for key, value in stream['methods'].iteritems():

						if not value.has_key('script'):
							return self.ConfigKeyErrorMsg('script', streamNum)

						if not value.has_key('format'):
							return self.ConfigKeyErrorMsg('format', streamNum)

						if not value.has_key('run'):
							self.ConfigKeyWarnMsg('run', streamNum)

						if not value.has_key('iteration'):
							self.ConfigKeyWarnMsg('iteration', streamNum)

						if value.has_key('plot'):
							if not value['plot']:
								return self.ConfigEmptyErrorMsg('plot', streamNum)
						else:
							self.ConfigKeyWarnMsg('plot', streamNum)

						if value.has_key('dataset'):
							if not value['dataset']:
								return self.ConfigEmptyErrorMsg('dataset', streamNum)
						else:
							return self.ConfigKeyErrorMsg('dataset', streamNum)

				except AttributeError, e:
					return self.ConfigKeyErrorMsg('methods', streamNum)

		Log.Info('Config file check: successful', self.verbose)