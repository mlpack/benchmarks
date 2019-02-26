'''
@file definitions.py
@author Anand Soni

Implementation of various metrics common to all classifiers.
'''

import sys
import numpy as np
import math

from modshogun import RealFeatures
from modshogun import MulticlassLabels
from modshogun import KNN, EuclideanDistance

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
    acc=0.0
    Sum=0
    l=len(CM)
    for i in range(l):
        for j in range(l):
            Sum+=CM[i][j]
        acc = acc + (float(CM[i][i])/float(Sum))*100.0
        Sum=0
    acc = acc/l
    return acc/100.0


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
    truePositives = CM[class_i][class_i]
    falsePositives = 0
    for j in range(l):
        falsePositives+=CM[j][class_i]
    falsePositives-=truePositives
    totalPositives = truePositives + falsePositives
    if totalPositives != 0:
      precision = truePositives/totalPositives
    else:
      #The class is not relevant (no predictions in this class)
      #All instances predicted as negative, no spurious cases
      precision = 1
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
     truePositives = CM[class_i][class_i]
     falseNegatives = 0
     for j in range(l):
         falseNegatives+=CM[class_i][j]
     falseNegatives-=truePositives
     total = truePositives + falseNegatives
     recall = truePositives/total
     return recall

  '''
  @param CM - The confusion matrix
  AvgPrecision(AvgRecall) represents the average of precisions(recall) obtained from each
  classifier. Since precision and recall are defined for binary classifiers, we
  can only calculate these measures for all the classes individually. AvgPrecision
  (AvgRecall) can be thought of as a new measure of performance for a multi-class
  classifier (One vs All approach).
  '''
  @staticmethod
  def AvgPrecision(CM):
    l=len(CM)
    avgPrecision = 0
    for i in range(l):
        avgPrecision+=Metrics.PrecisionForAClass(i,CM)
    avgPrecision = avgPrecision/l
    return avgPrecision

  @staticmethod
  def AvgRecall(CM):
    l=len(CM)
    avgRecall = 0
    for i in range(l):
        avgRecall+=Metrics.RecallForAClass(i,CM)
    avgRecall = avgRecall/l
    return avgRecall

  '''
  @param class_i - Index of the class in the confusion matrix
  @param CM - The confusion matrix
  FMeasure for a class is defined as the harmonic mean of precision and recall.
  '''
  @staticmethod
  def FMeasureClass(class_i,CM):
    l = len(CM)
    precClass = Metrics.PrecisionForAClass(class_i,CM)
    recClass = Metrics.RecallForAClass(class_i,CM)
    if (precClass + recClass) != 0:
      fMeasure = 2*precClass*recClass/(precClass+recClass)
    else:
      #Took care of the edge case here!
      truePositives = CM[class_i][class_i]
      falsePositives = 0
      for j in range(l):
        falsePositives+=CM[j][class_i]
      falsePositives-=truePositives
      falseNegatives=0
      for j in range(l):
        falseNegatives+=CM[class_i][j]
      falseNegatives-=truePositives
      trueNegatives=0
      #calculate trueNegatives
      for i in range(l):
        if i!=class_i:
          for j in range(l):
            trueNegatives+=CM[i][j]
          trueNegatives-=CM[i][class_i]
      fMeasure = 2*truePositives / (2*truePositives + falsePositives + falseNegatives)
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
    avgF = avgF/l
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
    pgt = 0
    #tgt - total greater than threshold
    tgt = 0
    total = 0
    for i in range(l):
      pgt = pgt + CM[class_i][i]
    pgt = (1/pgt) * CM[class_i][class_i]
    for j in range(l):
      tgt = tgt + CM[j][0]
    for i in range(l):
      for j in range(l):
        total = total + CM[i][j]
    tgt = tgt/total
    lift = pgt/tgt
    return lift


  '''
  @param CM - The confusion matrix
  Lift represents the ratio of the (%positives > threshold) to
  the (%total > threshold). Positive class decides the threshold.
  To convert this binary class measure into multi-class measure, we
  have used the LiftForAClass method to obtain Lifts for each class
  applying the One vs All technique.
  '''
  @staticmethod
  def LiftMultiClass(CM):
    AvgLift=0
    l=len(CM)
    for i in range(l):
      AvgLift+=Metrics.LiftForAClass(i,CM)
    AvgLift/=l
    return AvgLift


  '''
  @param class_i - Index of the class in the confusion matrix
  @param CM - The confusion matrix
  MCC is a balanced measure which returns values between +1 and -1.
  A coefficient of +1 represents a perfect prediction, 0 no better than random
  prediction and -1 indicates total disagreement between
  prediction and observation.
  '''
  @staticmethod
  def MatthewsCorrelationCoefficientClass(class_i, CM):
    l=len(CM)
    truePositives = CM[class_i][class_i]
    falsePositives = 0
    for j in range(l):
      falsePositives+=CM[j][class_i]
    falsePositives-=truePositives
    falseNegatives=0
    for j in range(l):
      falseNegatives+=CM[class_i][j]
    falseNegatives-=truePositives
    trueNegatives=0
    #calculate trueNegatives
    for i in range(l):
      if i!=class_i:
        for j in range(l):
          trueNegatives+=CM[i][j]
        trueNegatives-=CM[i][class_i]
    Numerator = (truePositives*trueNegatives) - (falsePositives*falseNegatives)
    Denominator=math.sqrt((truePositives + falsePositives)*
							(truePositives + falseNegatives)*
							(trueNegatives + falsePositives)*
							(trueNegatives + falseNegatives))
    if Denominator != 0:
      MCC = Numerator/Denominator
    else:
      #Class is not relevant (no predictions in this class)
      #The limiting case.
      MCC = 0
    return MCC


  '''
  @param CM - The confusion matrix
  MCC is a balanced measure which returns values between +1 and -1.
  A coefficient of +1 represents a perfect prediction, 0 no better
  than random prediction and -1 indicates total disagreement between
  prediction and observation. We use the MCC for a single class as
  obtained by applying the One vs All approach in the above method
  below.
  '''
  @staticmethod
  def MCCMultiClass(CM):
    MCC=0
    l=len(CM)
    for i in range(l):
      MCC+=Metrics.MatthewsCorrelationCoefficientClass(i,CM)
    MCC/=l
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
    #l : Number of classes
    l=len(CM)
    #trueVec : Vector/list with trueVec[index]=1 for the true class, 0 otherwise
    Vec = np.genfromtxt(truelabelFile,delimiter=',')
    instances=len(Vec)
    trueVec=[]
    for i in range(instances):
      vec=[]
      for j in range(l):
        vec.append(0)
      for j in range(l):
        vec[int(Vec[i])-1]=1
      trueVec.append(vec)
    #trueArray : 2D numpy array after converting trueVec
    trueArray=np.array(trueVec)
    print("True Vec : ",trueArray)
    #probVec : 2D numpy array with trueVec[index]=probability for the instance
    #to be in that class.
    probVec = np.genfromtxt(probabilities,delimiter=',')
    print("probVec : ", probVec)
    diffArray = trueArray - probVec
    print("diffArray : ",diffArray)
    #Quadratic Loss Function
    quadraticLoss=[]
    for i in range(len(diffArray)):
      squaredloss=0
      for j in range(len(diffArray[i])):
        squaredloss+=diffArray[i][j]*diffArray[i][j]
        quadraticLoss.append(squaredloss)
    quadraticLoss=np.array(quadraticLoss)
    print("quad loss : ",quadraticLoss)
	#Divide the total squared loss for each instance by the number of classes
    quadraticLoss = quadraticLoss/l
    totalLoss=0
    for i in range(len(quadraticLoss)):
      totalLoss+=quadraticLoss[i]
    totalLoss = totalLoss/instances
    print("tot loss : ",totalLoss)
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
  def MeanPredictiveInformationClass(class_i, truelabels, predictedlabels):
    predicted=np.genfromtxt(predictedlabels, delimiter=',')
    actual=np.genfromtxt(truelabels, delimiter=',')
    instances=len(actual)
    predictiveSum=0
    count=0
    for i in range(instances):
      if actual[i] == class_i:
        count+=1
        '''
        predictiveSum+=((actual[i] * math.log(predicted[i],2))+
						  ((1-actual[i]) * math.log(1-predicted[i],2)))
        We take actual[i] to be 0. Hence, the formula :
        We take 0.05 instead of absolute 0 and 0.95 instead of absolute 1
        to guarantee that an absolute 0 value doesn't become an argument
        to logarithm.
        '''
        predicted_val=0.05
        actual_val=0.05
        if predicted[i] != actual[i]:
          predicted_val = 0.95

        predictiveSum+=((actual_val*math.log(predicted_val,2)) + (predicted_val*math.log(1 - predicted_val,2)))

    if count != 0:
      predictiveSum/=count
    predictiveSum+=1
    return predictiveSum

  @staticmethod
  def MPIArrayClass(class_i, truelabels, predictedlabels):
    instances=len(truelabels)
    predictiveSum=0
    count=0
    for i in range(instances):
      if truelabels[i] == class_i:
        count+=1
        '''
        predictiveSum+=((actual[i] * math.log(predicted[i],2))+
						  ((1-actual[i]) * math.log(1-predicted[i],2)))
        We take actual[i] to be 0. Hence, the formula :
        We take 0.05 instead of absolute 0 and 0.95 instead of absolute 1
        to guarantee that an absolute 0 value doesn't become an argument
        to logarithm.
        '''
        predicted_val=0.05
        actual_val=0.05
        if predictedlabels[i] != truelabels[i]:
          predicted_val = 0.95

        predictiveSum+=((actual_val*math.log(predicted_val,2)) + (predicted_val*math.log(1 - predicted_val,2)))

    if count != 0:
      predictiveSum/=count
    predictiveSum+=1
    return predictiveSum

  '''
  This method extracts all the labels from the truelabels file in a list
  and returns this list. We can get the actual label value of a particular
  row in the CM using this list.
  '''
  @staticmethod
  def GetActualLabels(truelabels):
    labels=[]
    labels.append(truelabels[0])
    for i in range(len(truelabels)):
      if truelabels[i] not in labels:
        labels.append(truelabels[i])
    return labels


  '''
  @param CM - The confusion matrix
  @param truelabels - File with true labels for each instance
  @param predictedlabels - File with predicted label for each instance
  This is the average mean predictive information measure. We calculate
  MPI for each class applying the One vs All approach and take the average.
  '''
  @staticmethod
  def AvgMeanPredictiveInformation(CM, truelabels, predictedlabels):
    predicted=np.genfromtxt(predictedlabels, delimiter=',')
    actual=np.genfromtxt(truelabels, delimiter=',')
    mpi=0
    all_labels = Metrics.GetActualLabels(actual)
    for i in range(len(CM)):
      mpi+=Metrics.MeanPredictiveInformationClass(all_labels[i], truelabels, predictedlabels)
    mpi/=len(CM)
    return mpi

  '''
  @param CM - The confusion matrix
  @param truelabels - Array with true labels for each instance
  @param predictedlabels - Array with predicted label for each instance
  This is the average mean predictive information measure. We calculate
  MPI for each class applying the One vs All approach and take the average.
  '''
  @staticmethod
  def AvgMPIArray(CM, truelabels, predictedlabels):
    mpi=0
    all_labels = Metrics.GetActualLabels(truelabels)
    for i in range(len(CM)):
      mpi+=Metrics.MPIArrayClass(all_labels[i], truelabels, predictedlabels)
    mpi/=len(CM)
    return mpi

  '''
  @param truelabels - Array containing the true labels for the test data
  @param predictedlabels - Array containing the predicted labels for test data
  This method computes the Mean Squared Error based on the true labels and
  predicted labels from a classifier. We use this method when we donot get the
  required probabilities to compute quadratic loss function.
  '''
  @staticmethod
  def SimpleMeanSquaredError(truelabels, predictedlabels):
    simplemse = 0
    n = len(truelabels)
    for i in range(n):
      difference = truelabels[i] - predictedlabels[i]
      simplemse += difference * difference
    simplemse /= n
    return simplemse

  '''
  @param distance - Matrix containing learned distance.
  @param data - List containing data & true labels.
  @param k - Number of targets used calculation.
  @param flag - Switch to control whether to use distance weighted KNN or not.
  This method computes the accuracy based on the true labels and
  predicted labels from knn classifier.
  '''
  @staticmethod
  def KNNAccuracy(distance, data, k, flag):
    transformedData = np.dot(data[0], distance.T)
    feat  = RealFeatures(transformedData.T)
    labels = MulticlassLabels(data[1].astype(np.float64))
    dist = EuclideanDistance(feat, feat)
    knn = KNN(k + 1, dist, labels)
    knn.train(feat)
    # Get nearest neighbors.
    nn = knn.nearest_neighbors()
    nn = np.delete(nn, 0, 0)
    # Compute unique labels.
    uniqueLabels = np.unique(labels)
    # Keep count correct predictions.
    count = 0
    # Normalize labels
    for i in range(data[0].shape[0]):
      for j in range(len(uniqueLabels)):
        if (labels[i] == uniqueLabels[j]):
          labels[i] = j
          break

    for i in range(nn.shape[1]):
      mapLabels = [0 for x in range(len(uniqueLabels))]
      for j in range(nn.shape[0]):
        if (flag):
          distPoints = np.linalg.norm(data[0][nn[j][i],:] - data[0][i,:])
          # Add constant factor of 1 incase two points overlap
          mapLabels[int(labels[nn[j, i]])] += 1 / (distPoints + 1)**2
        else:
          # Subtract a variable factor to avoid draw condition without
          # affecting actual result.
          mapLabels[int(labels[nn[j, i]])] += 1 - j * 1e-8
      maxInd = np.argmax(mapLabels)
      if (maxInd == labels[i]):
        count += 1
    accuracy = (count / nn.shape[1]) * 100
    return accuracy
