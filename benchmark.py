'''
  @file benchmark.py
  @author Marcus Edel

  In this file we read the config file and start the benchmark or test the 
  config.
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
from system import *
from loader import * 
from parser import *

from optparse import OptionParser

def SystemInformation():
	# Show system informations.
	Log.Info('CPU Model: ' + SystemInfo.GetCPUModel())
	Log.Info('Distribution: ' + SystemInfo.GetDistribution())
	Log.Info('Platform: ' + SystemInfo.GetPlatform())
	Log.Info('Memory: ' + SystemInfo.GetMemory())
	Log.Info('CPU Cores: ' + SystemInfo.GetCPUCores())

def Main():
	# Read Config.
	config = Parser('config.yaml', verbose=False)

	# Iterate through all libraries.
	libraryMapping = config.GetConfigLibraryMethods()
	while libraryMapping:	

		# Iterate through all methods.
		methodMapping = config.GetConfigMethod(libraryMapping.methods)			
		while methodMapping and libraryMapping:

			if methodMapping.run:

				Log.Info('Method: ' + methodMapping.methodName)

				# Load script.
				module = Loader.ImportModuleFromPath(methodMapping.script)
				methodCall = getattr(module, methodMapping.methodName)

				for dataset in methodMapping.datasets:

					#! TEMPORARY
					# Create table.
					table = []
					# set table header.
					header = ['', libraryMapping.libraryName, 'matlab', 'shougun']
					table.append(header)		

					Log.Info('Options: ' + (dataset["options"] if dataset["options"] != '' 
						else 'None'))

					for files in dataset["files"]:

						row = ['-'] * 4;
						# Get dataset name.
						if  not isinstance(files, basestring):
							row[0] = os.path.splitext(os.path.basename(files[0]))[0]	
						else:
							row[0] = os.path.splitext(os.path.basename(files))[0]	

						Log.Info('Dataset: ' + row[0])

						time = 0
						for num in range(methodMapping.iteration):
							instance = methodCall(files, verbose=False)
							time += instance.RunMethod(dataset["options"]);

							# Call the destructor.
							del instance

						# Set time.
						row[1] = time / methodMapping.iteration
						table.append(row)

					# Show results in a table.
					Log.Notice('')
					Log.PrintTable(table)
					Log.Notice('')

			methodMapping = config.GetConfigMethod(libraryMapping.methods)
		libraryMapping = config.GetConfigLibraryMethods()

if __name__ == '__main__':
	parser = OptionParser(usage="usage: %prog [options] filename")
	parser.add_option("-t", "--test", action="store", dest="config",
			type="string", help="Don't run, just test the configuration file.")

	(options, args) = parser.parse_args()

	if options.config:
		config = Parser(options.config)
		config.CheckConfig()
	else:
		SystemInformation()
		Main()