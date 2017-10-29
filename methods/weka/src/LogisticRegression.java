/**
 * @file LogisticRegression.java
 * @author Anand Soni
 *
 * Logistic Regression with weka.
 */

import java.io.IOException;
import weka.core.*;
import weka.core.converters.ConverterUtils.DataSource;
import weka.core.converters.CSVLoader;
import weka.filters.Filter;
import weka.filters.unsupervised.attribute.NumericToNominal;

import java.io.File;
import java.io.FileWriter;
import java.io.BufferedWriter;
import java.util.HashMap;
import java.util.ArrayList;

/**
 * This class use the weka libary to implement Logistic Regression.
 */
public class LogisticRegression {
  private static final String USAGE = String
  .format("Logistic Regression.\n\n"
          + "Required options:\n"
          + "-t [string]     File containing X (regressors).\n"
          + "                The responses are assumed to be\n"
          + "                the last row of the input file.\n\n"
          + "Options:\n\n"
          + "-T [string]   Optional file containing containing\n"
          + "              test dataset\n"
          + "-m [int]      Maximum number of iterations\n");

  public static HashMap<Integer, Double> createClassMap(Instances Data) {
   HashMap<Integer, Double> classMap = new HashMap<Integer, Double>();
   int index = 0;
   for(int i = 0; i < Data.numInstances(); i++) {
    double cl = Data.instance(i).classValue();
    Double class_i = new Double(cl);
    if(!classMap.containsValue(class_i)) {
      Integer ind = new Integer(index);
      classMap.put(ind,class_i);
      index++;
    }
   }
   return classMap;
  }

  public static int maxProb(double[] probs) {
    double prediction = 0;
    int index = 0;
    for (int i = 0; i < probs.length; i++) {
      if(probs[i] >= prediction) {
        prediction = probs[i];
        index = i;
      }
    }
    return index;
  }

  public static void main(String args[]) {
    Timers timer = new Timers();
    try {
      // Get the data set path.
      String regressorsFile = Utils.getOption('t', args);
      if (regressorsFile.length() == 0)
        throw new IllegalArgumentException("Required option: File containing" +
            " the regressors.");

      // Load input dataset.
      DataSource source = new DataSource(regressorsFile);
      if (source.getLoader() instanceof CSVLoader)
        ((CSVLoader) source.getLoader()).setNoHeaderRowPresent(true);
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

      boolean hasMaxIters = false;
      int maxIter = Integer.parseInt(Utils.getOption('m', args));
      if (maxIter != 0)
        hasMaxIters = true;

      // Did the user pass a test file?
      String testFile = Utils.getOption('T', args);
      Instances testData = null;
      if (testFile.length() != 0)
      {
        source = new DataSource(testFile);
        if (source.getLoader() instanceof CSVLoader)
          ((CSVLoader) source.getLoader()).setNoHeaderRowPresent(true);
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
            myInstances.add(new DenseInstance(1.0,  new double[1]));

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

      HashMap<Integer, Double> classMap = createClassMap(data);
      // Perform Logistic Regression.
      timer.StartTimer("total_time");
      weka.classifiers.functions.Logistic model = new weka.classifiers.functions.Logistic();
      if (hasMaxIters)
        model.setMaxIts(maxIter);
      model.buildClassifier(data);

      // Use the testdata to evaluate the modell.
      if (testFile.length() != 0)
      {
        ArrayList<double[]> probabilityList = new ArrayList<double[]>();
        for (int i = 0; i < testData.numInstances(); i++)
        {
            probabilityList.add(model.distributionForInstance(testData.instance(i)));
        }

        try{
          File probabs = new File("weka_lr_probabilities.csv");
          if(!probabs.exists()) {
            probabs.createNewFile();
          }
          FileWriter writer = new FileWriter(probabs.getName(), false);

          File predictions = new File("weka_predicted.csv");
          if(!predictions.exists()) {
            predictions.createNewFile();
          }
          FileWriter writer_predict = new FileWriter(predictions.getName(), false);

          for (int i = 0; i < testData.numInstances(); i++)
          {
            double[] probabilities = probabilityList.get(i);
            String fdata = "";
            String predict = "";
            for(int k=0; k<probabilities.length; k++) {
              fdata = fdata.concat(String.valueOf(probabilities[k]));
              fdata = fdata.concat(",");
            }

            int predictionForInstance = maxProb(probabilities);
            Integer c_index = new Integer(predictionForInstance);
            Double predictedClass = classMap.get(c_index);
            writer.write(fdata);
            writer_predict.write(String.valueOf(predictedClass.doubleValue()) + "\n");
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
