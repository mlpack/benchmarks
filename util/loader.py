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
  '''
  @staticmethod
  def ImportModuleFromPath(path):

    if hasattr(os, 'getcwdu'):
      # Returns a Unicode object represantation.
      realPath = os.path.realpath(os.getcwdu())
    else:
      realPath = os.path.realpath(os.path.curdir)
      
    destinationPath = os.path.dirname(path)

    if destinationPath == '':
      destinationPath = '.'
      
    # Remove the .py suffix.
    scriptName = os.path.basename(path)

    if scriptName.endswith('.py'):
      modName = scriptName[:-3]
    else:
      modName = scriptName
      
    os.chdir(destinationPath)
    fileHandle = None
    try:
      tup = imp.find_module(modName, ['.'])
      module = imp.load_module(modName, *tup)
      fileHandle = tup[0]
    finally:
      os.chdir(realPath)
      if fileHandle is not None:
        fileHandle.close()

    # Return module name.
    return module