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


if __name__ == '__main__':

	# Show system informations.
	Log.Info('CPU Model: ' + SystemInfo.GetCPUModel())
	Log.Info('Distribution: ' + SystemInfo.GetDistribution())
	Log.Info('Platform: ' + SystemInfo.GetPlatform())
	Log.Info('Memory: ' + SystemInfo.GetMemory())
	Log.Info('CPU Cores: ' + SystemInfo.GetCPUCores())

	# Here we read the config file, but there is more work todo,
	# for that reason we define the necessary here.
	script = 'methods/mlpack/pca.py'
	datasets = ['datasets/cities.csv', 'datasets/faces.csv']
	method = 'PCA'

	# This is not part of the config but should be set correctly.
	mlpackPath = '/usr/local/bin/'

	# Create table.
	table = []
	# set table header.
	header = ['', 'mlpack', 'matlab', 'shougun']
	table.append(header)

	# Load script.
	module = Loader.ImportModuleFromPath('methods/mlpack/pca.py')
	Log.Info('Loading ' + script)
	methodCall = getattr(module, method)

	# Perform method on dataset.
	for dataset in datasets:
		row = ['-'] * 4;
		# Get dataset name.
		row[0] = os.path.splitext(os.path.basename(dataset))[0]

		# Perform PCA.
		Log.Info('Dataset: ' + row[0])
		instance = methodCall(dataset, path=mlpackPath)
		time = instance.RunMethod();

		# Delete instance and call the destructor.
		del instance

		# Set time.
		row[1] = time
		table.append(row)
	
	# Show results in a table.
	Log.Notice('')
	Log.PrintTable(table)