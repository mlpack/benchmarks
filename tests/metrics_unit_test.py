'''
  @file metrics_unit_test.py
  @author Anand Soni

  Test for the All Metrics scripts.
'''

import unittest

import os, sys, inspect


'''
Import the metrics path.
'''
metric_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], '../methods/metrics')))
if metric_subfolder not in sys.path:
  sys.path.insert(0, metric_subfolder)

from definitions import *
import numpy as np

class Metrics_Test(unittest.TestCase):

  '''
  Test Initialization
  '''
  def setUp(self):
    self.verbose = False
    self.CM = np.array([[11,19,15],
                        [0,35,10],
                        [10,10,25]])

  '''
  Test for the AverageAccuracy metric ((24.44 + 77.77 + 55.55) / 3 = 52.59 %)
  '''
  def test_AverageAcccuracy(self):
    result=Metrics.AverageAccuracy(self.CM)
    self.assertTrue(result > 52.0 and result < 52.6)

  '''
  Test for the AveragePrecision metric ((0.52 + 0.55 + 0.5)/3 = 0.5233)
  '''
  def test_AveragePrecision(self):
    result=Metrics.AvgPrecision(self.CM)
    self.assertTrue(result > 0.52 and result < 0.524)

  '''
  Test for the AverageRecall metric
  '''
  def test_AverageRecall(self):
    result=Metrics.AvgRecall(self.CM)
    self.assertTrue(result > 0.52 and result < 0.53)

  '''
  Test for the AvgFMeasure metric ((0.332 + 0.644 + 0.526)/3 = 0.507)
  '''
  def test_AverageFMeasure(self):
    result=Metrics.AvgFMeasure(self.CM)
    self.assertTrue(result > 0.5 and result < 0.51)

  '''
  Test for the LiftForAClass metric (5.0)
  '''
  def test_LiftForClass(self):
    result=Metrics.LiftForAClass(1,self.CM)
    self.assertTrue(result >= 5.0)

  '''
  Test for the LiftMultiClass metric (3.38)
  '''
  def test_LiftMultiClass(self):
    result=Metrics.LiftMultiClass(self.CM)
    self.assertTrue(result >= 3.0 and result <=3.39)

  '''
  Test for the MatthewsCorrelationCoefficientClass metric (0.43)
  '''
  def test_MatthewsCoefficient(self):
    result=Metrics.MatthewsCorrelationCoefficientClass(1,self.CM)
    self.assertTrue(result > 0.4 and result < 0.5)

  '''
  Test for MCCMultiClass metric (0.2915)
  '''
  def test_MCCMultiClass(self):
    result=Metrics.MCCMultiClass(self.CM)
    self.assertTrue(result > 0.28 and result <= 0.3)

  '''
  Test for the MeanSquaredError metric (0.5191)
  '''
  def test_MeanSquaredError(self):
    result=Metrics.MeanSquaredError("tests/true_labels.csv","tests/probabilities.csv",self.CM)
    self.assertTrue(result > 0.5 and result < 0.52)

  '''
  Test for the SimpleMeanSquaredError metric (1.34667)
  '''
  def test_SimpleMeanSquaredError(self):
    true_labels = np.genfromtxt("tests/true_labels.csv",delimiter=',')
    predicted_labels = np.genfromtxt("tests/predicted_labels.csv",delimiter=',')
    result=Metrics.SimpleMeanSquaredError(true_labels,predicted_labels)
    self.assertTrue(result > 1.33 and result < 1.35)

  '''
  Test for MeanPredictiveInformationClass(...) metric (-1.709)
  '''
  def test_MeanPredictiveInformationClass(self):
    result=Metrics.MeanPredictiveInformationClass(1, "tests/true_labels.csv", "tests/predicted_labels.csv")
    self.assertTrue(result > -1.75 and result <= -1.7)

  '''
  Test for AvgMeanPredictiveInformation(....) metric (-1.6537)
  '''
  def test_AvgMeanPredictiveInformation(self):
    result=Metrics.AvgMeanPredictiveInformation(self.CM, "tests/true_labels.csv", "tests/predicted_labels.csv")
    self.assertTrue(result > -1.7 and result <= -1.6)
