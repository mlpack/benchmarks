'''
  @file benchmark_linear_ridge_regression.py
  @author Ali Mohamed

  Test for the Linear Ridge Regression scripts.
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
Test the shogun Linear Ridge Regression script.
'''
class LinearRidgeRegression_SHOGUN_TEST(unittest.TestCase):

  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = ['datasets/abalone7_train.csv', 'datasets/abalone7_test.csv', 'datasets/abalone7_labels.csv']
    self.verbose = False
    self.timeout = 9000

    module = Loader.ImportModuleFromPath("methods/shogun/linear_ridge_regression.py")
    obj = getattr(module, "LinearRidgeRegression")
    self.instance = obj(self.dataset, verbose=self.verbose, timeout=self.timeout)

  '''
  Test the constructor.
  '''
  def test_Constructor(self):
    self.assertEqual(self.instance.verbose, self.verbose)
    self.assertEqual(self.instance.timeout, self.timeout)
    self.assertEqual(self.instance.dataset, self.dataset)

  '''
  Test the 'RunMetrics' function.
  '''
  def test_RunMetrics(self):
    result = self.instance.RunMetrics("-t 1.0")
    self.assertTrue(result["Simple MSE"] > 0)
    self.assertTrue(result["Runtime"] > 0)

'''
Test the scikit Linear Ridge Regression script.
'''
class LinearRidgeRegression_SCIKIT_TEST(unittest.TestCase):

  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = ['datasets/abalone7_train.csv', 'datasets/abalone7_test.csv', 'datasets/abalone7_labels.csv']
    self.verbose = False
    self.timeout = 9000

    module = Loader.ImportModuleFromPath("methods/scikit/linear_ridge_regression.py")
    obj = getattr(module, "LinearRidgeRegression")
    self.instance = obj(self.dataset, verbose=self.verbose, timeout=self.timeout)

  '''
  Test the constructor.
  '''
  def test_Constructor(self):
    self.assertEqual(self.instance.verbose, self.verbose)
    self.assertEqual(self.instance.timeout, self.timeout)
    self.assertEqual(self.instance.dataset, self.dataset)

  '''
  Test the 'RunMetrics' function.
  '''
  def test_RunMetrics(self):
    result = self.instance.RunMetrics("-t 1.0")
    self.assertTrue(result["Runtime"] > 0)
    self.assertTrue(result["Simple MSE"] > 0)


if __name__ == '__main__':
  unittest.main()
