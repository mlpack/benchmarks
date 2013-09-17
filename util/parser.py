'''
  @file parser.py
  @author Marcus Edel

  Class to parse and check the config file.
'''

import os
import sys
import inspect

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
    self.RUN = True
    self.ITERATION = 3
    self.OPTIONS = ''

    try:
      Log.Info("Load config file: " + config, verbose)
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
      stream = next(self.streams)
    except StopIteration as e:
      # We have to catch the exception to stop at the end. There exists no 
      # hasNext().
      return False

    if not "library" in stream:
        return self.KeyErrorMsg("library", streamNum)
    else:
      libraryName = stream["library"]
      Log.Info("Library: " + libraryName, self.verbose)

    if stream["library"] == "general":
      attr = collections.namedtuple("attributes", ["libraryName", "settings"])
      return attr(libraryName, stream["settings"].items())
    else:
      attr = collections.namedtuple("attributes", ["libraryName", "methods"])
      return attr(libraryName, stream["methods"].items())

  '''
  This method returns the attributes of a given method.

  @param methods - Contains the method attributes.
  @return A tuble that contains the method attributes.
  '''
  def GetConfigMethod(self, methods):
    try:
      method = list(methods)[self.mc]
      self.mc = self.mc + 1 
    except IndexError as e:
      # We have to catch the exception to stop at the end. There exists no 
      # hasNext().
      return False

    methodName = method[0]
    Log.Info("Method: " + methodName, self.verbose)

    attributes = method[1]

    # First check the required attributes. 
    if "script" in attributes:
      script = attributes["script"]
      Log.Info("Script: " + script, self.verbose)
    else:
      return self.KeyErrorMsg("script")

    if "format" in attributes:
      format = attributes["format"]
      Log.Info("Format: " + str(format), self.verbose)
    else:
      return self.gKeyErrorMsg('format')

    if "datasets" in attributes:
      datasets = attributes['datasets']
      for dataset in datasets:
        Log.Info("Dataset: " + str(dataset["files"]), self.verbose)
        if not "options" in dataset:
          dataset["options"] = self.OPTIONS
    else:
      return self.KeyErrorMsg("datasets")

    # Check the optional attributes. 
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

    attr = collections.namedtuple("attributes", ["methodName", "script", 
        "format", "datasets", "run", "iteration"])

    return attr(methodName, script, format, datasets, run, iteration)

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
  This function check if a script have the necessary class and the RunMethod 
  function. 

  @param methodName - The method name.
  @param methodScript - The script path and name.
  @return False if the script dosen't exist or the RunMethod method is not 
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
      if getattr(methodClass, "RunMethod", None):
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

              if "datasets" in value:
                if not value["datasets"]:
                  return self.EmptyErrorMsg("datasets", streamNum)
                else:
                  for dataset in value["datasets"]:

                    if not self.CheckIfAvailable(dataset["files"]):
                      return False

                    if not "options" in dataset:
                      self.KeyWarnMsg("options", streamNum)
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
    streamData = {}

    # Iterate through all libraries.
    libraryMapping = self.GetConfigLibraryMethods()
    while libraryMapping:
      if libraryMapping.libraryName == "general":
        streamData["general"] = libraryMapping.settings
      else:
        # Iterate through all methods.
        methodMapping = self.GetConfigMethod(libraryMapping.methods)
        while methodMapping and libraryMapping:
          # Collect data only from method with run value = true.
          if methodMapping.run:
            for dataset in methodMapping.datasets:

              # Extract the information from every section and saves the 
              # information into the dictionary.
              if methodMapping.methodName in streamData:
                tempDict = streamData[methodMapping.methodName]

                if dataset["options"] in tempDict:
                  t = (libraryMapping.libraryName, dataset["files"], 
                    methodMapping.iteration, methodMapping.script, 
                    methodMapping.format)  
                  tempDict[dataset["options"]].append(t)
                else:
                  t = (libraryMapping.libraryName, dataset["files"], 
                    methodMapping.iteration, methodMapping.script, 
                    methodMapping.format)
                  tempDict[dataset["options"]] = [t]
              else:
                d = {}
                t = (libraryMapping.libraryName, dataset["files"], 
                  methodMapping.iteration, methodMapping.script, 
                  methodMapping.format)
                d[dataset["options"]] = [t]
                streamData[methodMapping.methodName] = d

          methodMapping = self.GetConfigMethod(libraryMapping.methods)
      libraryMapping = self.GetConfigLibraryMethods()
      self.mc = 0

    return streamData
