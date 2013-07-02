'''
  @file test_benchmark.py
  @author Marcus Edel

  Test the configuration file.
'''


import os
import sys
import inspect

# Import the util path, this method even works if the path contains
# symlinks to modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], '../util')))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from parser import *

import argparse

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="""Test the configuration file.
      Check for correct syntax and then try to open files referred in the 
      configuration""")
  parser.add_argument('-c','--config', help='Configuration file name.', 
      required=True)

  args = parser.parse_args()

  if args:
    config = Parser(args.config)
    config.CheckConfig()