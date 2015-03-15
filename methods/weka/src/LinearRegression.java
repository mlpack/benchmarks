/**
 * @file LinearRegression.java
 * @author Marcus Edel
 *
 * Linear Regression with weka.
 */

import java.io.IOException;
import weka.core.*;
import weka.core.converters.ConverterUtils.DataSource;
import java.util.HashMap;
import weka.filters.Filter;
import weka.filters.unsupervised.attribute.NumericToNominal;

import java.io.File;
import java.io.FileWriter;
import java.io.BufferedWriter;

/**
 * This class use the weka libary to implement Linear Regression.
 */
public class LinearRegression {
  private static final String USAGE = String
  .format("Linear Regression.\n\n"
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

      // Transform numeric class to nominal class because the
      // classifier cannot handle numeric classes.
      NumericToNominal nm = new NumericToNominal();
      String[] options = new String[2];
      options[0] = "-R";
      options[1] = "last"; //set the attributes from indices 1 to 2 as
      nm.setOptions(options);
      nm.setInputFormat(data);
      data = Filter.useFilter(data, nm);

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

      // Set the class for the trainings set. The class is in the last row.
      if (data.classIndex() == -1)
        data.setClassIndex((data.numAttributes() - 1));

      // Are the responses in a separate file?
      String input_responsesFile = Utils.getOption('r', args);
      if (input_responsesFile.length() != 0)
      {
        // Merge the two datasets.
        source = new DataSource(input_responsesFile);
        Instances responses = source.getDataSet();
        data = Instances.mergeInstances(data ,responses);
      }

      // Set the class for the trainings set. The class is in the last row.
      if (data.classIndex() == -1)
        data.setClassIndex((data.numAttributes() - 1));

      // // Perform Linear Regression.
      timer.StartTimer("total_time");
      weka.classifiers.meta.ClassificationViaRegression model =
          new weka.classifiers.meta.ClassificationViaRegression();
      model.buildClassifier(data);

      // Use the testdata to evaluate the modell.
      if (testFile.length() != 0)
      {
        double[] predictions = new double[testData.numInstances()];
        for (int i = 0; i < testData.numInstances(); i++)
        {
            predictions[i] = model.classifyInstance(testData.instance(i));
        }

        timer.StopTimer("total_time");
        try {
          File predictionsFile = new File("weka_linreg_predictions.csv");
          if(!predictionsFile.exists()) {
            predictionsFile.createNewFile();
          }
          FileWriter writer_predict = new FileWriter(predictionsFile.getName(), false);

          for (int i = 0; i < testData.numInstances(); i++)
          {
            double prediction = predictions[i];
            String fdata = "";
            String predict = "";
            fdata = fdata.concat(String.valueOf(prediction));
            fdata = fdata.concat("\n");
            writer_predict.write(fdata);
          }
          writer_predict.close();
        } catch(Exception e) {
          e.printStackTrace();
        }
      }
      else
      {
        timer.StopTimer("total_time");
      }

      timer.PrintTimer("total_time");

    } catch (IOException e) {
      System.err.println(USAGE);
    } catch (Exception e) {
      e.printStackTrace();
    }
  }
}
