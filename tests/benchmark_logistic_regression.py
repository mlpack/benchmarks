'''
  @file benchmark_logistic_regression.py

  Test for the Logistic Regression Classifier scripts.
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
Test the Scikit Logistic Regression Classifier script.
'''
class LR_SCIKIT_TEST(unittest.TestCase):

  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = ['datasets/iris_train.csv', 'datasets/iris_test.csv']
    self.verbose = False
    self.timeout = 9000

    module = Loader.ImportModuleFromPath("methods/scikit/logistic_regression.py")
    obj = getattr(module, "LogisticRegression")
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
    result = self.instance.RunMetrics({})
    self.assertTrue(result["Runtime"] > 0)

'''
Test the Shogun Logistic Regression Classifier script.
'''
class LR_SHOGUN_TEST(unittest.TestCase):

  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = ['datasets/iris_train.csv', 'datasets/iris_test.csv','datasets/iris_labels.csv']
    self.verbose = False
    self.timeout = 9000

    module = Loader.ImportModuleFromPath("methods/shogun/logistic_regression.py")
    obj = getattr(module, "LogisticRegression")
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
    result = self.instance.RunMetrics({})
    self.assertTrue(result["Runtime"] > 0)


'''
Test the Milk Logistic Regression Classifier script.
'''
class LR_Milk_TEST(unittest.TestCase):

  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = ['datasets/iris_train.csv', 'datasets/iris_test.csv','datasets/iris_labels.csv']
    self.verbose = False
    self.timeout = 9000

    module = Loader.ImportModuleFromPath("methods/milk/logistic_regression.py")
    obj = getattr(module, "LogisticRegression")
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
    result = self.instance.RunMetrics({})
    self.assertTrue(result["Runtime"] > 0)

'''
Test the mlpack logistic regression classifier script.
'''
class lr_mlpack_test(unittest.TestCase):

  '''
  Initialization.
  '''
  def setUp(self):
    self.dataset = ['datasets/ecoli_train.csv', 'datasets/ecoli_test.csv',
        'datasets/ecoli_labels.csv']
    self.verbose = False
    self.timeout = 9000

    module = \
        Loader.ImportModuleFromPath("methods/mlpack/logistic_regression.py")
    obj = getattr(module, "LogisticRegression")
    self.instance = obj(self.dataset, verbose=self.verbose,
        timeout=self.timeout)

  '''
  Test the constructor.
  '''
  def testConstructor(self):
    self.assertEqual(self.instance.verbose, self.verbose)
    self.assertEqual(self.instance.timeout, self.timeout)
    self.assertEqual(self.instance.dataset, self.dataset)

  '''
  Test the RunMetrics() function.
  '''
  def testRunMetrics(self):
    result = self.instance.RunMetrics({})
    self.assertTrue(result['Runtime'] > 0)

if __name__ == '__main__':
  unittest.main()

