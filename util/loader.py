'''
  @file loader.py
  @author Marcus Edel

  Class to load modules and scripts.
'''

import imp
import os

'''
This class contains a function to import modules and scripts.
'''
class Loader(object):

  '''
  Import a module from a path.

  @param path - The path to the module.
  @return The name of the module.
  '''
  @staticmethod
  def ImportModuleFromPath(path):
    destinationPath = os.path.dirname(path)

    if destinationPath == "":
      destinationPath = '.'

    # Remove the .py suffix.
    scriptName = os.path.basename(path)

    if scriptName.endswith(".py"):
      modName = scriptName[:-3]
    else:
      modName = scriptName

    fileHandle = None
    try:
      tup = imp.find_module(modName, [destinationPath])
      module = imp.load_module(modName, *tup)
      fileHandle = tup[0]
    finally:
      if fileHandle is not None:
        fileHandle.close()

    # Return the name of the module.
    return module
