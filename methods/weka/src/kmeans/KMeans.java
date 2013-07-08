/**
 * @file KMeans.java
 * @author Marcus Edel
 *
 * K-Means Clustering with weka.
 */

import weka.clusterers.SimpleKMeans;
import weka.core.Instances;
import weka.core.Utils;
import weka.core.converters.ConverterUtils.DataSource;

/**
 * This class use the weka libary to implement K-Means Clustering.
 */
public class KMeans {

  private static final String USAGE = String
      .format("This program performs K-Means clustering on the given dataset.\n\n"
          + "Required options:\n"
          + "(-c) [int]         Number of clusters to find.\n"
          + "(-i) [string]      Input dataset to perform clustering on."
          + "-m) [int]          Maximum number of iterations before K-Means\n"
          + "                   terminates.  Default value 1000.\n"
          + "(-s) [int]         Random seed. ");

  public static void main(String args[]) {
    Timers timer = new Timers();
    try {
      // Get the data set path.
      String inputFile = Utils.getOption('i', args);
      if (inputFile.length() == 0)
        throw new IllegalArgumentException();
      
      // Load input dataset.
      DataSource source = new DataSource(inputFile);
      Instances data = source.getDataSet();
      
      // Create the KMeans object.
      SimpleKMeans kmeans = new SimpleKMeans();
      
      // Gather parameters and validation of options.
      String maxIteration = Utils.getOption('m', args);
      int m = 1000;
      if (maxIteration.length() != 0)
      {
        m = Integer.parseInt(maxIteration);
        if (m < 0)
        {
          System.out.println("[Fatal] Invalid value for maximum iterations(" + 
              maxIteration + ")! Must be greater than or equal to 0..");
          System.exit(-1);          
        }
        else if(m == 0)
        {
          m = Integer.MAX_VALUE;
        }
      }
      
      String clusters = Utils.getOption('c', args);
      if (clusters.length() == 0)
      {
        throw new IllegalArgumentException();
      }
      else
      {
        int c = Integer.parseInt(clusters);
        if (c < 1)
        {
          System.out.println("[Fatal] Invalid number of clusters requested (" + 
              clusters + ")! Must be greater than or equal to 1.");
          System.exit(-1);
        }
        
        kmeans.setNumClusters(c);
      }     
      
      String seed = Utils.getOption('s', args);
      if (seed.length() != 0)
        kmeans.setSeed(Integer.parseInt(seed));
            
      kmeans.setMaxIterations(m);     
      kmeans.setPreserveInstancesOrder(true);   
      
      // Perform K-Means clustering.
      timer.StartTimer("total_time");
      
      kmeans.buildClusterer(data);
      int[] assignments = kmeans.getAssignments();
      
      timer.StopTimer("total_time");
      timer.PrintTimer("total_time");
      
    } catch (IllegalArgumentException e) {
      System.err.println(USAGE);
    } catch (Exception e) {
      e.printStackTrace();
    }
  }

}
