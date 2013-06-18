'''
  @file benchmark.py
  @author Marcus Edel

  In this file we read the config file and start the benchmark.
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

if __name__ == '__main__':
	parser = OptionParser(usage="usage: %prog [options] filename")
	parser.add_option("-t", "--test", action="store", dest="config",
			type="string", help="Don't run, just test the configuration file.")

	(options, args) = parser.parse_args()

	if options.config:
		config = Parser(options.config)
		config.CheckConfig()
	else:
		# Read Config.
		config = Parser('config.yaml')

		# Show system informations.
		Log.Info('CPU Model: ' + SystemInfo.GetCPUModel())
		Log.Info('Distribution: ' + SystemInfo.GetDistribution())
		Log.Info('Platform: ' + SystemInfo.GetPlatform())
		Log.Info('Memory: ' + SystemInfo.GetMemory())
		Log.Info('CPU Cores: ' + SystemInfo.GetCPUCores())

		# Iterate through all libraries.
		libAttr = config.GetConfigLibraryMethods()
		while libAttr:		
			# Iterate through all methods.
			methAttr = config.GetConfigMethod(libAttr.methods)			
			while methAttr and libAttr:
				if methAttr.run:

					# Create table.
					table = []
					# set table header.
					header = ['', libAttr.libraryName, 'matlab', 'shougun']
					table.append(header)

					# Load script.
					module = Loader.ImportModuleFromPath(methAttr.script)
					methodCall = getattr(module, methAttr.methodName)

					# Perform method on dataset.
					for dataset in methAttr.dataset:
						row = ['-'] * 4;
						# Get dataset name.
						row[0] = os.path.splitext(os.path.basename(dataset))[0]

						# Perform PCA.
						Log.Info('Dataset: ' + row[0])
						time = 0
						for num in range(methAttr.iteration):
							instance = methodCall(dataset)
							time += instance.RunMethod();

							# Delete instance and call the destructor.
							del instance
							
						# Set time.
						row[1] = time / methAttr.iteration
						table.append(row)
					
					# Show results in a table.
					Log.Notice('')
					Log.PrintTable(table)

				methAttr = config.GetConfigMethod(libAttr.methods)
			libAttr = config.GetConfigLibraryMethods()