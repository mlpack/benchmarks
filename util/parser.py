'''
  @file parser.py
  @author Marcus Edel

  Class to parse and check the config file.
'''

import os
import sys
import inspect
import json

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from log import *
from loader import *

import yaml
import collections

'''
This class implements the parser to parse and check the config file.
'''
class Parser(object):

  '''
  Create the parser instance and load the config file.

  @param config - The config file name and path.
  @param verbose - Display informational messages.
  '''
  def __init__(self, config, verbose=True):
    self.verbose = verbose
    self.config = config
    self.mc = 0

    # Default values.
    self.RUN = []
    self.ITERATION = 3
    self.OPTIONS = {}
    self.ALIAS = 'None'
    self.WATCH = ['None']

    try:
      Log.Info("Load config file: " + config, verbose)

      # Parses the given stream and returns a sequence of Python objects
      # corresponding to the documents in the stream. In the following we will
      # iterate through the sequence with the next() operator.
      streams = yaml.load_all(open(config))
      self.streams = streams

    except IOError as e:
      Log.Fatal("Could not load config file: " + config)
    except yaml.YAMLError as exc:
      if hasattr(exc, "problem_mark"):
        mark = exc.problem_mark
        Log.Fatal("Error at position: (%s:%s)" % (mark.line+1, mark.column+1))

  '''
  This method returns the library information.

  @return Library name, methods attributes.
  '''
  def GetConfigLibraryMethods(self):
    try:
      # Get a single stream object from the sequence of stream objects.
      stream = next(self.streams)
    except StopIteration as e:
      # We have to catch the exception to stop at the end. There exists no
      # hasNext().
      return False

    # Check if the stream object contains the library key. If not return a key
    # error message.
    if not "library" in stream:
        return self.KeyErrorMsg("library", streamNum)
    else:
      # Get the value from the library key.
      libraryName = stream["library"]
      Log.Info("Library: " + libraryName, self.verbose)

    # Distinguish between a settings and a methods block. The general block
    # contains the settings block which contains all general settings.
    if stream["library"] == "general":
      # Generate a namedtuple with named fields (libraryName, settings). To get
      # the values from the tupel object we can call 'object.libraryName' and
      # 'object.settings'.
      attr = collections.namedtuple("attributes", ["libraryName", "settings"])
      # Store the values into the namedtuple. The second argument is a a list of
      # tuples: [('database', 'reports/benchmark.db'), ('gridColor', '#6E6E6E'),
      # ('timeout', 9000), ...].
      return attr(libraryName, stream["settings"].items())
    else:
      # Generate a namedtuple with named fields (libraryName, methods).
      attr = collections.namedtuple("attributes", ["libraryName", "methods"])
      # Store the values into the namedtuple. The second argument is a a list of
      # tuples with all information from the methods block.
      return attr(libraryName, stream["methods"].items())

  '''
  This method returns the attributes of a given method.

  @param methods - Contains the method attributes.
  @return A tuble that contains the method attributes.
  '''
  def GetConfigMethod(self, methods):
    try:
      # The methods object is a list of tuples that contains for every method
      # the corresponding method settings. E.g [ ('ALLKNN', settings),
      # ('KMEANS', settings), ...], we use the 'mc' value to get just a single
      # method form the list of tuples.
      method = list(methods)[self.mc]
      # Increase the 'mc' value to work with the next method in the followng
      # method call.
      self.mc = self.mc + 1
    except IndexError as e:
      # We have to catch the exception to stop at the end. There exists no
      # hasNext().
      return False

    # Get the method name form the list object.
    methodName = method[0]
    Log.Info("Method: " + methodName, self.verbose)

    # The second element contains all settings for the specified method.
    attributes = method[1]

    # First check the required attributes. If there isn't any value specified
    # return a error message.
    if "script" in attributes:
      script = attributes["script"]
      Log.Info("Script: " + script, self.verbose)
    else:
      return self.KeyErrorMsg("script")

    if "format" in attributes:
      format = attributes["format"]
      Log.Info("Format: " + str(format), self.verbose)
    else:
      return self.KeyErrorMsg('format')

    if "datasets" in attributes:
      datasets = attributes['datasets']
      for dataset in datasets:
        Log.Info("Dataset: " + str(dataset["files"]), self.verbose)

        if not "options" in dataset:
          dataset["options"] = self.OPTIONS

        if not "alias" in dataset:
          dataset["alias"] = self.ALIAS
    else:
      return self.KeyErrorMsg("datasets")

    # Check the optional attributes. Use the default values if there isn't any
    # values specified.
    if "run" in attributes:
      run = attributes["run"]
      Log.Info("Run: " + str(run), self.verbose)
    else:
      self.KeyWarnMsg("run")
      run = self.RUN

    if "iteration" in attributes:
      iteration = attributes["iteration"]
      Log.Info("Iteration: " + str(iteration), self.verbose)
    else:
      self.KeyWarnMsg("iteration")
      iteration = self.ITERATION

    if "watch" in attributes:
      watch = attributes["watch"]
      Log.Info("Watch: " + str(watch), self.verbose)
    else:
      self.KeyWarnMsg("watch")
      watch = self.WATCH

    # Generate a namedtuple with named fields (methodName, script, format, ...).
    attr = collections.namedtuple("attributes", ["methodName", "script",
        "format", "datasets", "run", "iteration", "watch"])

    # Store all values in the namedtuple.
    return attr(methodName, script, format, datasets, run, iteration, watch)

  '''
  Show emtpy value error message.

  @param key - The name of the key.
  @param streamNum - The number of the stream.
  @return False
  '''
  def EmptyErrorMsg(self, key, streamNum):
    Log.Fatal("Stream number: " + str(streamNum) + " the [" + key +
        "] list is empty.")
    return False

  '''
  Show a value is not set warn message.

  @param key - The name of the key.
  @param streamNum - The number of the stream.
  '''
  def KeyWarnMsg(self, key, streamNum=0):
    if streamNum == 0:
      Log.Warn("No [" + key + "] key, use default value.", self.verbose)
    else:
      Log.Warn("Stream number: " + str(streamNum) + " has no [" + key +
          "] key, use default value.", self.verbose)

  '''
  Show method is not callable warn message.

  @param methodName - The name of the method.
  @param methodScript - The path of the script.
  @param streamNum - The number of the stream.
  '''
  def CallableMethodWarnMsg(self, methodName, methodScript, streamNum):
    Log.Warn("Stream number: " + str(streamNum))
    Log.Warn("The method: " + methodName + " in script: " + methodScript
        + " is not callable.")

  '''
  Show file not available error message.

  @param fileName - The name of the file.
  @return False
  '''
  def NotAvailableErrorMsg(self, fileName):
    Log.Fatal("The file: " + fileName + " is not available.")
    return False

  '''
  This function check if a script have the necessary class and the RunTiming
  function.

  @param methodName - The method name.
  @param methodScript - The script path and name.
  @return False if the script dosen't exist or the RunTiming method is not
  available otherwise True.
  '''
  def CheckIfCallable(self, methodName, methodScript):
    try:
      with open(methodScript): pass
    except IOError:
      return False

    try:
      module = Loader.ImportModuleFromPath(methodScript)
    except Exception as e:
      Log.Warn("Exception: " + str(e))
      return False

    methodClass = getattr(module, methodName, None)
    if callable(methodClass):
      if getattr(methodClass, "RunTiming", None):
        return True

    return False

  '''
  This function checks if a file is readable.

  @param files - A list of files to check.
  @return The function returns True if the file is readable otherwise false.
  '''
  def CheckIfAvailable(self, files):
    def CheckDataset(dataset):
        try:
            with open(dataset): pass
        except IOError:
            return self.NotAvailableErrorMsg(datasets)
        return True

    for datasets in files:
      # Check if the value 'datasets' is a list of datasets.
      if not isinstance(datasets, str):
        for dataset in datasets:
          if not CheckDataset(dataset):
            return False
      else:
        if not CheckDataset(datasets):
            return False

    return True

  '''
  This function checks the config attributes and keys. The function checks also,
  if the script is runable and if the datasets are readable.

  @return The function returns False if the config file is not correct and the
  function shows some information to adjust the config. If the config is correct
  the function prints a successful message.
  '''
  def CheckConfig(self):
    Log.Info("Check config file: " + self.config, self.verbose)
    streamNum = 0
    for stream in self.streams:
      streamNum += 1

      if not "library" in stream:
        return self.KeyErrorMsg("library", streamNum)
      elif not "settings" in stream:
        if not "methods" in stream:
          return self.KeyErrorMsg("methods", streamNum)
        else:
          try:
            for key, value in stream["methods"].items():

              if not "script" in value:
                return self.KeyErrorMsg("script", streamNum)

              if not "format" in value:
                return self.KeyErrorMsg("format", streamNum)

              if not "run" in value:
                self.KeyWarnMsg("run", streamNum)

              if not "iteration" in value:
                self.KeyWarnMsg("iteration", streamNum)

              if not "watch" in value:
                self.KeyWarnMsg("watch", streamNum)

              if "datasets" in value:
                if not value["datasets"]:
                  return self.EmptyErrorMsg("datasets", streamNum)
                else:
                  for dataset in value["datasets"]:

                    if not self.CheckIfAvailable(dataset["files"]):
                      return False

                    if not "options" in dataset:
                      self.KeyWarnMsg("options", streamNum)

                    if not "alias" in dataset:
                      self.KeyWarnMsg("alias", streamNum)

              else:
                return self.KeyErrorMsg("datasets", streamNum)

              if not self.CheckIfCallable(key, value["script"]):
                self.CallableMethodWarnMsg(key, value["script"], streamNum)

          except AttributeError as e:
            return self.KeyErrorMsg("methods", streamNum)

    Log.Info("Config file check: successful", self.verbose)

  '''
  Merge the streams and create a dictionary which contains the data.

  @return Dictionary with all informations.
  '''
  def StreamMerge(self):
    # Create a python dictionary (key/value store) to store te data from the
    # config file.
    streamData = {}

    # Iterate through all libraries.
    libraryMapping = self.GetConfigLibraryMethods()

    # Iterate through all libary blocks until libraryMapping is False.
    while libraryMapping:
      # Check if the stream data is a general block. Use the namedtuple function
      # to get the 'libraryName' value.
      if libraryMapping.libraryName == "general":
        # Store the general block settings in the dictionary. Afterwards we can
        # use the 'general' key to access the data.
        streamData["general"] = libraryMapping.settings

      # Right now we distinguish between a general block and a library block. So
      # if the block isn't a general block its a library block.
      else:
        # Iterate through all methods. With the following line we get the first
        # method.
        methodMapping = self.GetConfigMethod(libraryMapping.methods)
        while methodMapping and libraryMapping:
          # Collect data only from method with 'run' value = true.
          if methodMapping.run:
            # We use the 'datasets' field from the named tuple to iterate
            # through all datasets an the corresponding settings. The dataset
            # value is a key/value structure that looks like:
            # {'files': ['datasets/iris.csv', 'datasets/wine.csv'],
            # 'options': ''}.
            for dataset in methodMapping.datasets:
              # Double-check for valid options: make sure there are not two
              # sweep() calls in a single method.
              sweeps = ["sweep" in str(v) for k, v in
                  dataset["options"].items()].count(True)
              if sweeps > 1:
                Log.Fatal("Options " + str(dataset["options"]) + " invalid:" +
                    " only one sweep allowed per method block!")
                raise Exception("only one sweep allowed per method block")

              # Extract the information from every section and store the
              # information into the dictionary. First check if the 'streamData'
              # key/value store already contains the information for a given
              # method name. The method name (e.g. KPCA) is the key for all
              # information from all libraries that implements the method
              # (e.g. KPCA).
              # To access the values for the given method (e.g. KPCA) we store
              # everything in a second dictionary an store that in the main
              # key,value structure.
              #
              # The structure of the second dictionary looks like:
              # {'KPCA': d}
              # d = {'-k linear': [('mlpack', ['datasets/circle_data.csv'], 3,
              # 'methods/mlpack/kernel_pca.py', ['csv', 'txt'])]}
              if methodMapping.methodName in streamData:
                # The main key/value already contains a dictionary with the
                # given method name as key (e.g. KPCA). In this case we use the
                # dictionary and just add the new information.
                # Get the dictionary with the method name as key (e.g. KPCA).
                tempDict = streamData[methodMapping.methodName]

                # We sort the libraries with the same method by the option which
                # are specified in the config file. So we check if the option is
                # already in the second dictionary.
                if json.dumps(dataset["options"]) in tempDict:
                  # Append the information for the library to the already defined
                  # option.
                  t = (libraryMapping.libraryName, dataset["files"],
                    methodMapping.iteration, methodMapping.script,
                    methodMapping.format, methodMapping.run, dataset["alias"],
                    methodMapping.watch)
                  tempDict[json.dumps(dataset["options"])].append(t)

                # This is are new options for the specified method name. So we
                # create the new entry for the option.
                else:
                  # Store the infromation for the specified method name with the
                  # option values as key.
                  t = (libraryMapping.libraryName, dataset["files"],
                    methodMapping.iteration, methodMapping.script,
                    methodMapping.format, methodMapping.run, dataset["alias"],
                    methodMapping.watch)
                  tempDict[json.dumps(dataset["options"])] = [t]

              # Create the second dictionary if it doesn't exist.
              else:
                d = {}
                # Store the settings for the given method in a tuple.
                t = (libraryMapping.libraryName, dataset["files"],
                  methodMapping.iteration, methodMapping.script,
                  methodMapping.format, methodMapping.run, dataset["alias"],
                  methodMapping.watch)

                # To access the method options we can use the options key.
                # Since the options is a dict, we'll just encode it as a string.
                d[json.dumps(dataset["options"])] = [t]
                # Store the initial second dictionary with the method name as
                # key (e.g. KPCA) in the main key/value store.
                streamData[methodMapping.methodName] = d
                print(streamData)

          methodMapping = self.GetConfigMethod(libraryMapping.methods)
      libraryMapping = self.GetConfigLibraryMethods()
      self.mc = 0

    return streamData
