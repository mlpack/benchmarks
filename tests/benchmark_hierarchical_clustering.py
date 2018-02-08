'''
  @file benchmark_hierarchical_clustering.py
  @author Chirag Pabbaraju

  Test for the Hierarchical clustering script
'''

import unittest
import sys
import os
import inspect

# Import the util path, this method even works if the path contains symlinks to modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from loader import *

'''
Test the Shogun Hierarchical clustering script
'''
class HIERARCHICAL_CLUSTERING_SHOGUN_TEST(unittest.TestCase):
  '''
  Test initialization.
  '''
  def setUp(self):
    self.dataset = "datasets/iris.csv"
    self.verbose = False
    self.timeout = 9000
    module = Loader.ImportModuleFromPath("methods/shogun/hierarchical_clustering.py")
    obj = getattr(module, "HierarchicalClustering")
    self.instance = obj(self.dataset, verbose=self.verbose, timeout=self.timeout)

  '''
  Test the constructor
  '''
  def test_Constructor(self):
    self.assertEqual(self.instance.dataset, self.dataset)
    self.assertEqual(self.instance.verbose, self.verbose)
    self.assertEqual(self.instance.timeout, self.timeout)

  '''
  Test the RunMetrics function.
  '''
  def test_RunMetrics(self):
    result = self.instance.RunMetrics({ "merges" : 3 , "distance" : "euclidean" })
    self.assertTrue(result["Runtime"] > 0)


if __name__ == "__main__":
  unittest.main()
  