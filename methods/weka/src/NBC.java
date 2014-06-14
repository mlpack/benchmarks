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

import java.io.File;
import java.io.FileWriter;
import java.io.BufferedWriter;
//import java.io.Exception;

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

  public static void getProbabilities(Classifier model, Instances testData) {
    double[] probs;
    try{
        File probabilities = new File("weka_probabilities.csv");
        if(!probabilities.exists()) {
          probabilities.createNewFile();
        }
        FileWriter writer = new FileWriter(probabilities.getName(),true);
        //BufferedWriter Bwriter = new BufferedWriter(writer);
        int l=0,i=0;
        for (i = 0; i < testData.numInstances(); i++) {
          probs = model.distributionForInstance(testData.instance(i));
          String data="";
          for(l=0; l<probs.length; l++) {
            String inst = Double.toString(probs[l]);
            data = data.concat(inst);
            data = data.concat(",");
          }
          writer.write(data);
          writer.write("\n");
        }
        writer.write(Integer.toString(i));
        writer.close();
      }catch(Exception e) {
        e.printStackTrace();
      }
  }
  
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
      
      // Get the probabilities.
      getProbabilities(cModel,testData);

      // Run Naive Bayes Classifier on the test dataset.
      // Write predicted class values for each intance to 
      // benchmarks/weka_predicted.csv.
      double prediction = 0;
      try{
        File predictedlabels = new File("weka_predicted.csv");
        if(!predictedlabels.exists()) {
          predictedlabels.createNewFile();
        }
        FileWriter writer = new FileWriter(predictedlabels.getName(),true);
        //BufferedWriter Bwriter = new BufferedWriter(writer);
        int i;
        for (i = 0; i < testData.numInstances(); i++)
          prediction = cModel.classifyInstance(testData.instance(i));
          String pred = Double.toString(prediction);
          writer.write(pred);
          writer.write("\n");
        writer.write(Integer.toString(i));
        writer.close();
      } catch(Exception e) {
        e.printStackTrace();
      }
      timer.StopTimer("total_time");
      timer.PrintTimer("total_time");
      
    } catch (IllegalArgumentException e) {
          System.err.println(USAGE);
      } catch (Exception e) {
        e.printStackTrace();
      } 
  }
}
