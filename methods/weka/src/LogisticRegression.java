/**
 * @file LogisticRegression.java
 * @author Anand Soni
 *
 * Logistic Regression with weka.
 */

import java.io.IOException;
import weka.core.*;
import weka.core.converters.ConverterUtils.DataSource;

import java.io.File;
import java.io.FileWriter;
import java.io.BufferedWriter;
/**
 * This class use the weka libary to implement Logistic Regression.
 */
public class LogisticRegression {
  private static final String USAGE = String
  .format("Logistic Regression.\n\n"
          + "Required options:\n"
          + "-i [string]     File containing X (regressors).\n"
          + "                The responses are assumed to be\n"
          + "                the last row of the input file.\n\n"
          + "Options:\n\n"
          + "-t [string]   Optional file containing containing\n"
          + "              test dataset");
  
  public static double maxProb(double[] probs) {
    double prediction=0;
    for (int i=0; i < probs.length; i++) {
      if(probs[i] >= prediction) prediction=probs[i];
    }
    return prediction;
  }
  
  public static void main(String args[]) {
    Timers timer = new Timers();
    try {
      // Get the data set path.
      String regressorsFile = Utils.getOption('i', args);
      if (regressorsFile.length() == 0)
        throw new IllegalArgumentException("Required option: File containing" +
            " the regressors.");
      
      // Load input dataset.
      DataSource source = new DataSource(regressorsFile);
      Instances data = source.getDataSet();
      
      // Did the user pass a test file?
      String testFile = Utils.getOption('t', args);
      Instances testData = null;
      if (testFile.length() != 0)
      {
        source = new DataSource(testFile);
        testData = source.getDataSet();

        // Weka makes the assumption that the structure of the training and test
        // sets are exactly the same. This means that we need the exact same 
        // number of attributes. So we need to add a new attribute to the test 
        // set if this differs from the trainig set.
        if (data.numAttributes() > testData.numAttributes())
        {
          // Create a new nominal attribute.
          FastVector attributes = new FastVector(1);
          attributes.addElement(new Attribute("nominal", new FastVector(1)));
          Instances myInstances = new Instances("dummy", attributes, testData.numInstances());

          // Add some dummy data to the new attribute.
          for (int i = 0; i < testData.numInstances(); i++) 
            myInstances.add(new Instance(1.0,  new double[1]));

          // Merge the new dummy attribute with the testdata set.
          testData = Instances.mergeInstances(testData, myInstances);
        }

        // Set the class index for the testdata set. This isn't used in the 
        // evaluation process.
        if (testData.classIndex() == -1)
          testData.setClassIndex((testData.numAttributes() - 1));
      }      
      
      // Set the class fro the trainings set. The class is in the last row.
      if (data.classIndex() == -1)
        data.setClassIndex((data.numAttributes() - 1));

      // Perform Logistic Regression.
      timer.StartTimer("total_time");
      weka.classifiers.functions.Logistic model = new weka.classifiers.functions.Logistic();
      model.buildClassifier(data);

      // Use the testdata to evaluate the modell.
      if (testFile.length() != 0)
      {
        try{
          File probabs = new File("weka_lr_probabilities.csv");
          if(!probabs.exists()) {
            probabs.createNewFile();
          }
          FileWriter writer = new FileWriter(probabs.getName(), false);
          
          File predictions = new File("weka_lr_predictions.csv");
          if(!predictions.exists()) {
            predictions.createNewFile();
          }
          FileWriter writer_predict = new FileWriter(predictions.getName(), false);

          for (int i = 0; i < testData.numInstances(); i++) 
          {
            double[] probabilities = model.distributionForInstance(testData.instance(i));
            String data="";
            String predict="";
            for(int k=0; k<probabilities.length; k++) {
              data.concat(String.valueOf(probabilities[k]));
              data.concat(",");
            }
            double predictionForInstance = maxProb(probabilities);
            writer.write(data);
            writer_predict.write(String.valueOf(predictionForInstance));
          }
          writer.close();
          writer_predict.close();
        }catch(Exception e) {
          e.printStackTrace();
        }
      }
      
      timer.StopTimer("total_time");
      timer.PrintTimer("total_time");
      
    } catch (IOException e) {
      System.err.println(USAGE);
    } catch (Exception e) {
      e.printStackTrace();
    }   
  }
}
