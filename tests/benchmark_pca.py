'''
  @file benchmark_pca.py
  @author Marcus Edel

  Test for the Principal Components Analysis scripts.
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
Test the mlpack Principal Components Analysis script.
'''
class PCA_MLPACK_TEST(unittest.TestCase):

  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = "datasets/iris.csv"
    self.verbose = False
    self.timeout = 9000

    module = Loader.ImportModuleFromPath("methods/mlpack/pca.py")
    obj = getattr(module, "PCA")
    self.instance = obj(self.dataset, verbose=self.verbose, timeout=self.timeout)
  
  '''
  Test the constructor.
  '''
  def test_Constructor(self):
    # The mlpack script should set the description value.
    self.assertTrue(self.instance.description != "")
    self.assertEqual(self.instance.verbose, self.verbose)
    self.assertEqual(self.instance.timeout, self.timeout)
    self.assertEqual(self.instance.dataset, self.dataset)

  '''
  Test the 'RunMethod' function.
  '''
  def test_RunMethod(self):
    result = self.instance.RunMethod("")
    self.assertTrue(result > 0)

  '''
  Test the 'RunMemoryProfiling' function.
  '''
  def test_RunMemoryProfiling(self):
    result = self.instance.RunMemoryProfiling("", "test.mout")
    self.assertEqual(result, None)
    os.remove("test.mout")
  
  '''
  Test the destructor.
  '''
  def test_Destructor(self):
    del self.instance

    clean = True
    filelist = ["gmon.out", "output.csv"]
    for f in filelist:
      if os.path.isfile(f):
        clean = False

    self.assertTrue(clean)

'''
Test the weka Principal Components Analysis script.
'''
class PCA_WEKA_TEST(unittest.TestCase):

  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = "datasets/iris.csv"
    self.verbose = False
    self.timeout = 9000

    module = Loader.ImportModuleFromPath("methods/weka/pca.py")
    obj = getattr(module, "PCA")
    self.instance = obj(self.dataset, verbose=self.verbose, timeout=self.timeout)
  
  '''
  Test the constructor.
  '''
  def test_Constructor(self):
    self.assertEqual(self.instance.verbose, self.verbose)
    self.assertEqual(self.instance.timeout, self.timeout)
    self.assertEqual(self.instance.dataset, self.dataset)

  '''
  Test the 'RunMethod' function.
  '''
  def test_RunMethod(self):
    result = self.instance.RunMethod("")
    self.assertTrue(result > 0)

'''
Test the shogun Principal Components Analysis script.
'''
class PCA_SHOGUN_TEST(unittest.TestCase):

  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = "datasets/iris.csv"
    self.verbose = False
    self.timeout = 9000

    module = Loader.ImportModuleFromPath("methods/shogun/pca.py")
    obj = getattr(module, "PCA")
    self.instance = obj(self.dataset, verbose=self.verbose, timeout=self.timeout)
  
  '''
  Test the constructor.
  '''
  def test_Constructor(self):
    self.assertEqual(self.instance.verbose, self.verbose)
    self.assertEqual(self.instance.timeout, self.timeout)
    self.assertEqual(self.instance.dataset, self.dataset)

  '''
  Test the 'RunMethod' function.
  '''
  def test_RunMethod(self):
    result = self.instance.RunMethod("")
    self.assertTrue(result > 0)

'''
Test the scikit Principal Components Analysis script.
'''
class PCA_SCIKIT_TEST(unittest.TestCase):

  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = "datasets/iris.csv"
    self.verbose = False
    self.timeout = 9000

    module = Loader.ImportModuleFromPath("methods/scikit/pca.py")
    obj = getattr(module, "PCA")
    self.instance = obj(self.dataset, verbose=self.verbose, timeout=self.timeout)
  
  '''
  Test the constructor.
  '''
  def test_Constructor(self):
    self.assertEqual(self.instance.verbose, self.verbose)
    self.assertEqual(self.instance.timeout, self.timeout)
    self.assertEqual(self.instance.dataset, self.dataset)

  '''
  Test the 'RunMethod' function.
  '''
  def test_RunMethod(self):
    result = self.instance.RunMethod("")
    self.assertTrue(result > 0)

'''
Test the mlpy Principal Components Analysis script.
'''
class PCA_MLPY_TEST(unittest.TestCase):

  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = "datasets/iris.csv"
    self.verbose = False
    self.timeout = 9000

    module = Loader.ImportModuleFromPath("methods/mlpy/pca.py")
    obj = getattr(module, "PCA")
    self.instance = obj(self.dataset, verbose=self.verbose, timeout=self.timeout)
  
  '''
  Test the constructor.
  '''
  def test_Constructor(self):
    self.assertEqual(self.instance.verbose, self.verbose)
    self.assertEqual(self.instance.timeout, self.timeout)
    self.assertEqual(self.instance.dataset, self.dataset)

  '''
  Test the 'RunMethod' function.
  '''
  def test_RunMethod(self):
    result = self.instance.RunMethod("")
    self.assertTrue(result > 0)

'''
Test the matlab Principal Components Analysis script.
'''
class PCA_MATLAB_TEST(unittest.TestCase):

  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = "datasets/iris.csv"
    self.verbose = False
    self.timeout = 9000

    module = Loader.ImportModuleFromPath("methods/matlab/pca.py")
    obj = getattr(module, "PCA")
    self.instance = obj(self.dataset, verbose=self.verbose, timeout=self.timeout)
  
  '''
  Test the constructor.
  '''
  def test_Constructor(self):
    self.assertEqual(self.instance.verbose, self.verbose)
    self.assertEqual(self.instance.timeout, self.timeout)
    self.assertEqual(self.instance.dataset, self.dataset)

  '''
  Test the 'RunMethod' function.
  '''
  def test_RunMethod(self):
    result = self.instance.RunMethod("")
    self.assertTrue(result > 0)

if __name__ == '__main__':
  unittest.main()
