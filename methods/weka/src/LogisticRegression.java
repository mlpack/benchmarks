/**
 * @file LogisticRegression.java
 * @author Anand Soni
 *
 * Logistic Regression with weka.
 */

import java.io.IOException;
import weka.core.*;
import weka.core.converters.ConverterUtils.DataSource;

/**
 * This class use the weka libary to implement Logistic Regression.
 */
public class LogisticRegression {
  private static final String USAGE = String
  .format("Logistic Regression.\n\n"
          + "Required options:\n"
          + "-i [string]     File containing X (regressors).\n\n"
          + "Options:\n\n"
          + "-r [string]   Optional file containing y (responses).\n"
          + "              If not given, the responses are assumed\n"
          + "              to be the last row of the input file.");
  
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
      
      // Are the responses in a separate file?
      String input_responsesFile = Utils.getOption('r', args);
      if (regressorsFile.length() != 0)
      {
        // Merge the two datasets.
        source = new DataSource(input_responsesFile);
        Instances responses = source.getDataSet();          
        data = Instances.mergeInstances(data ,responses);     
      }
      
      // The class is in the last row.
      data.setClassIndex((data.numAttributes() - 1));     
      
      // Perform Logistic Regression.
      timer.StartTimer("total_time");
      weka.classifiers.functions.Logistic model = new weka.classifiers.functions.Logistic();
      model.buildClassifier(data);
      double[] b = model.coefficients();  
      
      timer.StopTimer("total_time");
      timer.PrintTimer("total_time");
      
    } catch (IOException e) {
      System.err.println(USAGE);
    } catch (Exception e) {
      e.printStackTrace();
    }   
  }
}
