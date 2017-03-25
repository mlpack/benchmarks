'''
  @file benchmark_gmm.py
  @author Marcus Edel

  Test for the Gaussian Mixture Model scripts.
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
Test the shogun Gaussian Mixture Model script.
'''
class GMM_SHOGUN_TEST(unittest.TestCase):

  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = "datasets/iris.csv"
    self.verbose = False
    self.timeout = 9000

    module = Loader.ImportModuleFromPath("methods/shogun/gmm.py")
    obj = getattr(module, "GMM")
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
    result = self.instance.RunMetrics("")
    self.assertTrue(result["Runtime"] > 0)

'''
Test the scikit Gaussian Mixture Model script.
'''
class GMM_SCIKIT_TEST(unittest.TestCase):

  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = "datasets/iris.csv"
    self.verbose = False
    self.timeout = 9000

    module = Loader.ImportModuleFromPath("methods/scikit/gmm.py")
    obj = getattr(module, "GMM")
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
    print("asdw")
    result = self.instance.RunMetrics("")
    print("result" + str(result))
    # self.assertTrue(result > 0)

if __name__ == '__main__':
  unittest.main()
