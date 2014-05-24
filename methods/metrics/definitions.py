'''
    @file definitions.py
    @author Anand Soni

    Implementation of various metrics common to all classifiers.
'''

from __future__ import print_function
import re
import sys

class Metrics(object):
	
  '''
  @param labels - File containing true labels 
  @param prediction - File containing predicted labels 
  Create the confusion matrix from the two arrays containing the true labels and
  the predicted labels. The confusion matrix contains all information about the
  number of true and false positives and negatives for all the classes in 
  consideration.
  '''
  @staticmethod 
  def ConfusionMatrix(labels, prediction):
      from sklearn.metrics import confusion_matrix
      return confusion_matrix(labels, prediction)
 
  '''
  @param CM - The confusion matrix
  This function is a great and simple one that can be used as a debugging tool
  for metrics involving true/false positives/negatives. Uncomment the call to 
  this function in RunMetrics(..) to see the Confusion Matrix visually!
  '''
  @staticmethod
  def VisualizeConfusionMatrix(CM):
      import pylab as pl
      print(CM)
      pl.matshow(CM)
      pl.title('Confusion Matrix')
      pl.colorbar()
      pl.ylabel('True Label')
      pl.xlabel('Predicted Label')
      pl.show()

  '''
  @param CM - The confusion matrix
  Average accuracy measure. The average accuracy is defined as the average/mean
  of accuracies of prediction obtained for each class in consideration. We use
  the confusion matrix as the parameter to this function.
  '''
  @staticmethod
  def AverageAccuracy(CM):
      acc=0
      Sum=0
      l=len(CM)
      for i in range(l):
          for j in range(l):
              Sum+=CM[i][j]
          acc = acc + (CM[i][i]/Sum)*100
          Sum=0
      return acc/l


  '''
  @param class_i - Index of the class in the confusion matrix
  @param CM - The confusion matrix
  Precision measure for a single class. Arguments provided to this method are the
  confusion matrix and the class index in the confusion matrix (class_i). It is not
  the actual label for the class.
  '''
  @staticmethod
  def PrecisionForAClass(class_i,CM):
      l=len(CM)
      truePositives=CM[class_i][class_i]
      falsePositives=0
      for j in range(l):
          falsePositives+=CM[j][class_i]
      totalPositives=truePositives+falsePositives
      precision=truePositives/totalPositives
      return precision

  '''
  @param class_i - Index of the class in the confusion matrix
  @param CM - The confusion matrix
  Recall measure for a single class. Arguments provided to this method are the
  confusion matrix and the class index in the confusion matrix (class_i). It is not
  the actual label for the class.
  '''
  @staticmethod
  def RecallForAClass(class_i,CM):
      l=len(CM)
      truePositives=CM[class_i][class_i]
      falseNegatives=0
      for j in range(l):
          falseNegatives+=CM[class_i][j]
      total=truePositives+falseNegatives
      recall=truePositives/total
      return recall

  '''
  @param CM - The confusion matrix
  AvgPrecision(AvgRecall) represents the average of precisions obtained from each
  classifier. Since precision and recall are defined for binary classifiers, we 
  can only calculate these measures for all the classes individually. AvgPrecision
  (AvgRecall) can be thought of as a new measure of performance for a multi-class 
  classifier.
  '''
  @staticmethod
  def AvgPrecision(CM):
      l=len(CM)
      avgPrecision=0
      for i in range(l):
          precisionForClass=Metrics.PrecisionForAClass(i,CM)
          avgPrecision+=precisionForClass
      avgPrecision=avgPrecision/l
      return avgPrecision
  
  @staticmethod
  def AvgRecall(CM):
      l=len(CM)
      avgRecall=0
      for i in range(l):
          recallForClass=Metrics.RecallForAClass(i,CM)
          avgRecall+=recallForClass
      avgRecall=avgRecall/l
      return avgRecall

  '''
  @param class_i - Index of the class in the confusion matrix
  @param CM - The confusion matrix
  FMeasure for a class is defined as the harmonic mean of precision and recall.
  '''
  @staticmethod
  def FMeasureClass(class_i,CM):
      precClass=Metrics.PrecisionForAClass(class_i,CM)
      recClass=Metrics.RecallForAClass(class_i,CM)
      fMeasure = 2*precClass*recClass/(precClass+recClass)
      return fMeasure

  '''
  @param CM - The confusion matrix
  AvgFMeasure represents the average of FMeasures of all the classes in 
  consideration.
  '''
  @staticmethod
  def AvgFMeasure(CM):
      l=len(CM)
      avgF=0
      for i in range(l):
          avgF+=Metrics.FMeasureClass(i,CM)
      avgF=avgF/l
      return avgF
   
  '''
  @param class_i - Index of the class in the confusion matrix
  @param CM - The confusion matrix
  Lift represents the ratio of the (%positives > threshold) to 
  the (%total > threshold). Positive class decides the threshold. 
  '''
  @staticmethod
  def LiftForAClass(class_i,CM):
	  l=len(CM)
	  #pgt - positives greater than threshold
	  pgt=0
	  #tgt - total greater than threshold
	  tgt=0
	  total=0
	  for i in range(l):
		  pgt=pgt+CM[class_i][i]
	  pgt=(1/pgt)*CM[class_i][class_i]
	  for j in range(l):
		  tgt=tgt+CM[j][0]
	  for i in range(l):
		  for j in range(l):
			  total=total+CM[i][j]
	  tgt=tgt/total
	  lift=pgt/tgt
	  return lift	   
   
  '''
  @param class_i - Index of the class in the confusion matrix
  @param CM - The confusion matrix
  MCC is a balanced measure which returns values between +1 and -1.
  A coefficient of +1 represents a perfect prediction, 0 no better 
  than random prediction and −1 indicates total disagreement between 
  prediction and observation. 
  '''
  @staticmethod 		
  def MatthewsCorrelationCoefficientClass(class_i, CM):
	  import math	
	  l=len(CM)
	  truePositives=CM[class_i][class_i]
	  falsePositives=0
	  for j in range(l):
		  falsePositives+=CM[j][class_i]
	  falseNegatives=0
	  for j in range(l):
		  falseNegatives+=CM[class_i][j]
	  trueNegatives=0
	  #calculate trueNegatives
	  Numerator=(truePositives*trueNegatives)-(falsePositives*falseNegatives)
	  Denominator=math.sqrt((truePositives+falsePositives)*(truePositives+falseNegatives)*(trueNegatives+falsePositives)*(trueNegatives+falseNegatives))
	  MCC=Numerator/Denominator
	  return MCC
	   	
  '''
  @param truelabelFile - Name of the file which contains the true label
  for the instance
  @param probabilities - Name of the file which contains the probabilities
  for that instance to be in a particular class (CSV)
  @param CM - The confusion matrix
  Mean squared error for classifiers which return probabilities can be 
  implemented in terms of the Quadratic Loss function as defined below.
  '''
  @staticmethod 		
  def MeanSquaredError(truelabelFile, probabilities, CM):
	  import numpy as np
	  import math
	  #l : Number of classes
	  l=len(CM)
	  #trueVec : Vector/list with trueVec[index]=1 for the true class, 0 otherwise
	  Vec=np.genfromtxt(truelabelFile,delimiter=',')
	  instances=len(Vec)
	  trueVec=[]
	  for i in range(instances):
		  vec=[]
		  for j in range(l):
			  vec.append(0)
		  vec[int(Vec[i])-1]=1
		  trueVec.append(vec)
	  #trueArray : 2D numpy array after converting trueVec
	  trueArray=np.array(trueVec)
	  #probVec : 2D numpy array with trueVec[index]=probability for the instance to be in that class.
	  probVec=np.genfromtxt(probabilities,delimiter=',')
	  diffArray=trueArray-probVec
	  #Quadratic Loss Function
	  quadraticLoss=[]
	  for i in range(len(diffArray)):
		  squaredloss=0
		  for j in range(len(diffArray[i])):
			  squaredloss+=diffArray[i][j]*diffArray[i][j]
		  quadraticloss.append(squaredloss)
	  quadraticloss=np.array(quadraticloss)
	  #Divide the total squared loss for each instance by the number of classes
	  quadraticloss=quadraticloss/l
	  totalLoss=0
	  for i in range(len(quadraticloss)):
		  totalLoss+=quadraticloss[i]
	  totalLoss=totalLoss/instances
	  return totalLoss
		   
  
  '''
  @param truelabels - Name of the file which contains the true label
  for the instance
  @param predictedlabels - Name of the file which contains the predicted
  labels for the instance
  Mean predictive information is a metric closely related to cross
  entropy and conveniently gives easily interpretable results.
  The below implementation is only for binary classifiers. 
  '''
  @staticmethod 		
  def MeanPredictiveInformation(truelabels, predictedlabels):
	  import numpy as np
	  import math
	  predicted=np.genfromtxt(predictedlabels, delimiter=',')
	  actual=np.genfromtxt(truelabels, delimiter=',')
	  instances=len(actual)
	  predictiveSum=0
	  for i in range(instances):
		  predictiveSum+=((actual[i]*math.log(predicted[i],2))+((1-actual[i])*math.log(1-predicted[i],2)))
	  predictiveSum/=instances
		  
		
