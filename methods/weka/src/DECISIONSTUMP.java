/**
 * @file DECISIONSTUMP.java
 *
 * Decision Stump with weka.
 */

import weka.classifiers.Classifier;
import weka.classifiers.RandomizableClassifier;
import weka.classifiers.trees.DecisionStump;
import weka.core.Instances;
import weka.core.Utils;
import weka.core.converters.ConverterUtils.DataSource;
import weka.filters.Filter;
import weka.filters.unsupervised.attribute.NumericToNominal;
import java.io.File;
import java.io.FileWriter;
import java.io.BufferedWriter;
import weka.core.Attribute;
import java.util.List;
import java.util.ArrayList;
/**
 * This class use the weka libary to implement Decision Stump.
 */
public class DECISIONSTUMP {

  private static final String USAGE = String
      .format("This program trains the Decision Stump on the given\n"
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

      // Use the last row of the training data as the labels.
      trainData.setClassIndex((trainData.numAttributes() - 1));
      DataSource testsource = new DataSource(testFile);
      Instances testData = testsource.getDataSet();

      // Add pseudo class to the test set if no class information is provided.
      if (testData.numAttributes() < trainData.numAttributes()) {
        List<String> labelslist = new ArrayList<String>();
        for (int i = 0; i < trainData.classAttribute().numValues(); i++) {
          labelslist.add(trainData.classAttribute().value(i));
        }

        testData.insertAttributeAt(new Attribute("class", labelslist),
            testData.numAttributes());
      }

      // Use the last row of the training data as the labels.
      testData.setClassIndex((testData.numAttributes() - 1));

      timer.StartTimer("total_time");
      // Create and train the classifier.
      Classifier cModel = (Classifier)new DecisionStump();
      cModel.buildClassifier(trainData);

      // Run Decision Stump on the test dataset.
      // Write predicted class values for each intance to
      // benchmarks/weka_predicted.csv.
      double prediction = 0;
      try{
        File predictedlabels = new File("weka_predicted.csv");
        if(!predictedlabels.exists()) {
          predictedlabels.createNewFile();
        }
        FileWriter writer = new FileWriter(predictedlabels.getName(), false);

        for (int i = 0; i < testData.numInstances(); i++) {
          prediction = cModel.classifyInstance(trainData.instance(i));
          String pred = Double.toString(prediction);
          writer.write(pred);
          writer.write("\n");
        }

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
