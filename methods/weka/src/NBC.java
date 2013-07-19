/**
 * @file NBC.java
 * @author Marcus Edel
 *
 * Naive Bayes Classifier with weka.
 */

import weka.classifiers.Classifier;
import weka.classifiers.bayes.NaiveBayes;
import weka.core.Instances;
import weka.core.Utils;
import weka.core.converters.ConverterUtils.DataSource;
import weka.filters.Filter;
import weka.filters.unsupervised.attribute.NumericToNominal;

/**
 * This class use the weka libary to implement Naive Bayes Classifier.
 */
public class NBC {
  
  private static final String USAGE = String
      .format("This program trains the Naive Bayes classifier on the given\n"
      + "labeled training set and then uses the trained classifier to classify\n"
      + "the points in the given test set.\n\n"
      + "Required options:\n"
      + "-T [string]     A file containing the test set.\n"
      + "-t [string]     A file containing the training set.");
  
  public static void main(String args[]) {
  Timers timer = new Timers();    
    try {
      // Get the data set path.
      String trainFile = Utils.getOption('t', args);
      String testFile = Utils.getOption('T', args);
      if (trainFile.length() == 0 || testFile.length() == 0)
        throw new IllegalArgumentException();
        
      // Load train and test dataset. 
      DataSource source = new DataSource(trainFile);
      Instances trainData = source.getDataSet();
      
      // Transform numeric class to nominal class because the 
      // classifier cannot handle numeric classes.
      NumericToNominal nm = new NumericToNominal();
      String[] options = new String[2];
      options[0] = "-R";
      options[1] = "last"; //set the attributes from indices 1 to 2 as
      nm.setOptions(options);
      nm.setInputFormat(trainData);
      trainData = Filter.useFilter(trainData, nm);
      
      // Use the last row of the training data as the labels.
      trainData.setClassIndex((trainData.numAttributes() - 1));      
      
      source = new DataSource(testFile);
      Instances testData = source.getDataSet(); 
      // Use the last row of the training data as the labels.
      testData.setClassIndex((testData.numAttributes() - 1));
      
      timer.StartTimer("total_time");
      // Create and train the classifier.   
      Classifier cModel = (Classifier)new NaiveBayes();
      cModel.buildClassifier(trainData);
      
      // Run Naive Bayes Classifier on the test dataset.
      double prediction;
      for (int i = 0; i < testData.numInstances(); i++)
        prediction = cModel.classifyInstance(testData.instance(i));
      
      timer.StopTimer("total_time");
      timer.PrintTimer("total_time");
      
    } catch (IllegalArgumentException e) {
          System.err.println(USAGE);
      } catch (Exception e) {
        e.printStackTrace();
      } 
  }
}
