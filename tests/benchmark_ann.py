'''
  @file benchmark_ann.py

  Test for the Approximate Nearest Neighbors benchmark scripts.
'''

import unittest

import os, sys, inspect

# Import the util path, this method even works if the path contains
# symlinks to modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], '../util')))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from loader import *

'''
Test the annoy ANN script.
'''
class ANN_ANNOY_TEST(unittest.TestCase):

  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = ['datasets/iris_train.csv', 'datasets/iris_test.csv',
        'datasets/iris_labels.csv']
    self.verbose = False
    self.timeout = 9000

    module = Loader.ImportModuleFromPath("methods/annoy/ann.py")
    obj = getattr(module, "ANN")
    self.instance = obj(self.dataset, timeout=self.timeout)

  '''
  Test the constructor.
  '''
  def test_Constructor(self):
    self.assertEqual(self.instance.timeout, self.timeout)
    self.assertEqual(self.instance.dataset, self.dataset)

  '''
  Test the 'RunMetrics' function.
  '''
  def test_RunMetrics(self):
    result = self.instance.RunMetrics("-k 10 -n 10")
    self.assertTrue(result["Runtime"] > 0)

if __name__ == '__main__':
  unittest.main()

