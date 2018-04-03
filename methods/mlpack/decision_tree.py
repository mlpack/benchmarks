"""
  @file decision_tree.py
  @author Xu Kaiqiang

  Class to benchmark the mlpack decision tree classification method.
  Here I'd like to clarify more info on this benchmark.
  Usually, this file will be give parameters such as train_dataset(including labels as last column),
  test_dataset, test_labels, which are stored in self.dataset
  
"""


import os
import sys
import inspect
import numpy as np

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

# Import the metrics definitions path.
metrics_folder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../metrics")))
if metrics_folder not in sys.path:
    sys.path.insert(0, metrics_folder)

from util.log import *
from definitions import Metrics
from util.misc import *
import shlex

try:
  import subprocess32 as subprocess
except ImportError:
  import subprocess

import re
import collections

class DTC(object):
    """
    This class implements the Decision Tree Classifier benchmark.
    """

    def __init__(self, dataset, timeout, path=os.environ['BINPATH'],
                 verbose=True, debug=os.environ["DEBUGBINPATH"]):
        """
        Create the Decision Tree Classifier benchmark instance.

        @param dataset - Input dataset to perform DTC on. Attention: usually, 
        `dataset` is composed of training_set, testing_set, and labels set of the latter.
        @param timeout - The time until the timeout. Default no timeout.
        @param verbose - Display informational messages.
        """
        self.verbose = verbose
        self.dataset = dataset
        self.path = path
        self.timeout = timeout
        self.debug = debug

        cmd = shlex.split(self.path + "mlpack_decision_tree -h")
        try:
            s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False)
        except Exception as e:
            Log.Fatal("Could not execute command: " + str(cmd))
        else:
            pattern = re.compile(br"""(.*?)Required.*?options:""",
                                 re.VERBOSE | re.MULTILINE | re.DOTALL)
            match = pattern.match(s)
            if not match:
                Log.Warn("Can't parse description,", self.verbose)
                description = ""
            else:
                description = match.group(1)

            self.description = description

    def __del__(self):
        """
        Destructor to clean up model and output file at the end.
        :return: 
        """
        files = ['mlpack_dct_predict.csv']
        for f in files:
            if os.path.isfile(f):
                os.remove(f)

    def RunMetrics(self, options):
        """
        Perform decision tree prediction. 
        mlpack_decision_tree -t dataset[0] -T dataset[1]
        If the method has been successfully completed, it returns the elapsed time in seconds
        :param options: extra options for the method
        :return: elapsedtime in seconds or a negative value if the method failed
        """
        Log.Info("Perform Decision Tree Training and Prediction", self.verbose)

        if len(options) > 0:
            Log.Fatal("Unknown parameters: " + str(options))
            raise Exception("unknown parameters")

        # In this case dataset[0] includes training_set and labels_set(as last column),
        # and dataset[1],dataset[2] are test_set and test_labels respectively.
        if len(self.dataset) >= 2:

            cmd = shlex.split(self.path + "mlpack_decision_tree -t " +
                              self.dataset[0] + " -T " + self.dataset[1] +
                              " -v " + " -p " + " mlpack_dct_predict.csv")
        else:
            Log.Fatal("This benchmarking logic is using at least 2 files including training set(last column as labels)\
             testing set. And labels of testing set is optional.")
        try:
            s = subprocess.check_output(cmd, stderr=subprocess.STDOUT,shell=False,
                                        timeout=self.timeout)
        except subprocess.TimeoutExpired as e:
            Log.Warn(str(e))
            return -2
        except Exception as e:
            Log.Fatal("Could not execute command: " + str(cmd) + " The error is: " + str(e))
            return -1
        metrics = {}
        timer = self.parseTimer(s)
        if timer != -1:
            metrics["Runtime"] = timer.total_time - timer.loading_data - timer.saving_data
            Log.Info(("total time: %fs" % (metrics['Runtime'])), self.verbose)
        if len(self.dataset) >= 3:
            truelabels = LoadDataset(self.dataset[2])
            predictions = LoadDataset('mlpack_dct_predict.csv')
            confusionMatrix = Metrics.ConfusionMatrix(truelabels, predictions)
            metrics['ACC'] = Metrics.AverageAccuracy(confusionMatrix)
            metrics['MCC'] = Metrics.MCCMultiClass(confusionMatrix)
            metrics['Precision'] = Metrics.AvgPrecision(confusionMatrix)
            metrics['Recall'] = Metrics.AvgRecall(confusionMatrix)
            metrics['MSE'] = Metrics.SimpleMeanSquaredError(truelabels, predictions)
        return metrics

    def parseTimer(self, data):
        """
        Parse the timer data form a given string.
    
        @param data - String to parse timer data from.
        @return - Namedtuple that contains the timer data or -1 in case of an error.
        :param data: 
        :return: 
        """
        # Compile the regular expression pattern into a regular expression object to
        # parse the timer data.
        pattern = re.compile(br"""
          .*?loading_data: (?P<loading_data>.*?)s.*?
          .*?saving_data: (?P<saving_data>.*?)s.*?
          .*?total_time: (?P<total_time>.*?)s.*?
          """, re.VERBOSE | re.MULTILINE | re.DOTALL)

        match = pattern.match(data)
        if not match:
            Log.Fatal("Can't parse the data: wrong format")
            return -1
        else:
            # Create a namedtuple and return the timer data.
            timer = collections.namedtuple('timer', ["loading_data", "total_time", "saving_data"])
            return timer(float(match.group("loading_data")),
                         float(match.group("total_time")), float(match.group("saving_data")))

