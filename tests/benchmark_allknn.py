'''
  @file benchmark_allknn.py
  @author Marcus Edel

  Test for the All K-Nearest-Neighbors scripts.
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
Test the mlpack All K-Nearest-Neighbors script.
'''
class ALLKNN_MLPACK_TEST(unittest.TestCase):

  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = "datasets/wine.csv"
    self.verbose = False
    self.timeout = 9000

    module = Loader.ImportModuleFromPath("methods/mlpack/allknn.py")
    obj = getattr(module, "ALLKNN")
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
    result = self.instance.RunMethod("-k 3")
    self.assertTrue(result > 0)
  
  '''
  Test the 'RunMemoryProfiling' function.
  '''
  def test_RunMemoryProfiling(self):
    result = self.instance.RunMemoryProfiling("-k 3", "test.mout")
    self.assertEqual(result, None)
    os.remove("test.mout")

  '''
  Test the destructor.
  '''
  def test_Destructor(self):
    del self.instance

    clean = True
    # At the end none of these files should be available.
    filelist = ["gmon.out", "distances.csv", "neighbors.csv"]
    for f in filelist:
      if os.path.isfile(f):
        clean = False

    self.assertTrue(clean)

'''
Test the matlab All K-Nearest-Neighbors script.
'''
class ALLKNN_MATLAB_TEST(unittest.TestCase):

  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = "datasets/wine.csv"
    self.verbose = False
    self.timeout = 9000

    module = Loader.ImportModuleFromPath("methods/matlab/allknn.py")
    obj = getattr(module, "ALLKNN")
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
    result = self.instance.RunMethod("-k 3")
    self.assertTrue(result > 0)

'''
Test the mlpy All K-Nearest-Neighbors script.
'''
class ALLKNN_MLPY_TEST(unittest.TestCase):

  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = "datasets/wine.csv"
    self.verbose = False
    self.timeout = 9000

    module = Loader.ImportModuleFromPath("methods/mlpy/allknn.py")
    obj = getattr(module, "ALLKNN")
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
    result = self.instance.RunMethod("-k 3")
    self.assertTrue(result > 0)

'''
Test the scikit All K-Nearest-Neighbors script.
'''
class ALLKNN_SCIKIT_TEST(unittest.TestCase):

  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = "datasets/wine.csv"
    self.verbose = False
    self.timeout = 9000

    module = Loader.ImportModuleFromPath("methods/scikit/allknn.py")
    obj = getattr(module, "ALLKNN")
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
    result = self.instance.RunMethod("-k 3")
    self.assertTrue(result > 0)

'''
Test the shogun All K-Nearest-Neighbors script.
'''
class ALLKNN_SHOGUN_TEST(unittest.TestCase):

  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = "datasets/wine.csv"
    self.verbose = False
    self.timeout = 9000

    module = Loader.ImportModuleFromPath("methods/shogun/allknn.py")
    obj = getattr(module, "ALLKNN")
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
    result = self.instance.RunMethod("-k 3")
    self.assertTrue(result > 0)

'''
Test the weka All K-Nearest-Neighbors script.
'''
class ALLKNN_WEKA_TEST(unittest.TestCase):

  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = "datasets/wine.csv"
    self.verbose = False
    self.timeout = 9000

    module = Loader.ImportModuleFromPath("methods/weka/allknn.py")
    obj = getattr(module, "ALLKNN")
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
    result = self.instance.RunMethod("-k 3")
    self.assertTrue(result > 0)

if __name__ == '__main__':
  unittest.main()
