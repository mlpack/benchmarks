/**
 * @file PCA.java
 * @author Marcus Edel
 *
 * Principal Components Analysis with weka.
 */

import weka.core.Instances;
import weka.core.Utils;
import weka.core.converters.ConverterUtils.DataSource;
import weka.attributeSelection.AttributeSelection;
import weka.attributeSelection.PrincipalComponents;
import weka.attributeSelection.Ranker;

/**
 * This class use the weka libary to implement Principal Components Analysis.
 */
public class PCA {

  private static final String USAGE = String
      .format("This program performs principal components analysis on the given"
      + "dataset.\nIt will transform the data onto its principal components, "
      + "optionally performing\ndimensionality reduction by ignoring the "
      + "principal components with the\nsmallest eigenvalues.\n\n"
      + "Required options:\n"
      + "-i [string]     Input dataset to perform PCA on.\n\n"
      + "Options:\n\n"
      + "-d [int]    Desired dimensionality of output dataset. If -1,\n"
      + "            no dimensionality reduction is performed.\n"
      + "            Default value -1.\n"
      + "-s          If set, the data will be scaled before running\n"
      + "            PCA, such that the variance of each feature is 1.");

  public static void main(String args[]) {
    Timers timer = new Timers();
    try {
      // Get the data set path.
      String dataset = Utils.getOption('i', args);
      if (dataset.length() == 0)
        throw new IllegalArgumentException();

      timer.StartTimer("total_time");
      timer.StartTimer("loading_data");

      // Load input dataset.
      DataSource source = new DataSource(dataset);
      Instances data = source.getDataSet();

      timer.StopTimer("loading_data");

      // Find out what dimension we want.
      int k = 0;
      String dimension = Utils.getOption('d', args);
      if (dimension.length() == 0) {
        k = data.numAttributes();
      } else {
        k = Integer.parseInt(dimension);
        // Validate the parameter.
        if (k > data.numAttributes()) {
          System.out.printf("[Fatal] New dimensionality (%d) cannot be greater"
              + "than existing dimensionality (%d)!'\n", k, 
              data.numAttributes());
          
          System.exit(-1);
        }
      }

      // Performs a principal components analysis.
      PrincipalComponents pcaEvaluator = new PrincipalComponents();

      // Sets the amount of variance to account for when retaining principal 
      // components.
      pcaEvaluator.setVarianceCovered(1.0);
      // Sets maximum number of attributes to include in transformed attribute 
      // names.
      pcaEvaluator.setMaximumAttributeNames(-1);

      // Scaled X such that the variance of each feature is 1.
      boolean scale = Utils.getFlag('s', args);
      if (scale) {
        pcaEvaluator.setCenterData(true);
      } else {
        pcaEvaluator.setCenterData(false);
      }

      // Ranking the attributes.
      Ranker ranker = new Ranker();
      // Specify the number of attributes to select from the ranked list.
      ranker.setNumToSelect(k - 1);

      AttributeSelection selector = new AttributeSelection();
      selector.setSearch(ranker);
      selector.setEvaluator(pcaEvaluator);
      selector.SelectAttributes(data);

      // Transform data into eigenvector basis.
      Instances transformedData = selector.reduceDimensionality(data);

      timer.StopTimer("total_time");

      timer.PrintTimer("loading_data");
      timer.PrintTimer("total_time");

    } catch (IllegalArgumentException e) {
      System.err.println(USAGE);
    } catch (Exception e) {
      e.printStackTrace();
    }
  }
}
