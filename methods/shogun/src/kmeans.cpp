/**
 * @file kmeans.hpp
 * @author Ryan Curtin
 *
 * K-Means (with initial centroids) Clustering with shogun.
 */
#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <iomanip>
#include <ctime>

#include <shogun/base/init.h>

#define private protected
#include <shogun/clustering/KMeans.h>
#undef private
#include <shogun/distance/EuclideanDistance.h>
#include <shogun/features/DenseFeatures.h>
#include <shogun/features/RealFileFeatures.h>
#include <shogun/io/AsciiFile.h>

using namespace shogun;

// Define a new KMeans class with the opportunity to set initial centroids.
class KMeans : public CKMeans
{
public:
  KMeans(int32_t k_, CDistance* d) : CKMeans(k_, d) { }
  
  // Overload the train_machine function, to set initial centroids.
  virtual bool train_machine(CFeatures* data, CDenseFeatures<float64_t>* centroids)
  {
    ASSERT(distance);
    
    if (data)
      distance->init(data, data);
    
    ASSERT(distance->get_feature_type() == F_DREAL);
    
    CDenseFeatures<float64_t>* lhs = (CDenseFeatures<float64_t>*)
    distance->get_lhs();
    
    ASSERT(lhs);
    int32_t num = lhs->get_num_vectors();
    SG_UNREF(lhs);
    
    Weights = SGVector<float64_t>(num);
    for (int32_t i = 0; i < num; ++i)
      Weights.vector[i] = 1.0;
    
    clustknb(true, centroids->get_feature_matrix().matrix);
    
    return true;
  }
};

int main(int argc, char** argv)
{
  init_shogun_with_defaults();
  
  // Load input dataset.
  const char* dataset = argv[1];
  const char* centroids = argv[2];
  int32_t clusters = atoi(argv[3]);
  int32_t maxIterations = atoi(argv[4]);
  
  CAsciiFile* dfile = new CAsciiFile(dataset);
  SGMatrix<float64_t> dmat = SGMatrix<float64_t>();
  dmat.load(dfile);
  SG_UNREF(dfile);
  
  CAsciiFile* cfile = new CAsciiFile(centroids);
  SGMatrix<float64_t> cmat = SGMatrix<float64_t>();
  cmat.load(cfile);
  SG_UNREF(cfile);
  
  CDenseFeatures<float64_t>* data = new CDenseFeatures<float64_t>(dmat);
  SG_REF(data);
  
  CDenseFeatures<float64_t>* cent = new CDenseFeatures<float64_t>(cmat);
  SG_REF(cent);
  
  CEuclideanDistance* dist = new CEuclideanDistance(data, data);
  
  timeval start;
  start.tv_sec = 0;
  start.tv_usec = 0;
  
  gettimeofday(&start, NULL);
  
  // Perform K-Means clustering.
  KMeans k(clusters, dist);
  k.set_max_iter(maxIterations);
  k.train_machine(data, cent);  
  
  timeval end;
  gettimeofday(&end, NULL);
  
  timeval delta;
  timersub(&end, &start, &delta);
  
  std::cout << "[INFO ]   total_time:" << delta.tv_sec << "." << std::setw(6)
  << std::setfill('0') << delta.tv_usec << "s" << std::endl;
  
  SG_UNREF(data);
  SG_UNREF(cent);
  
  exit_shogun();
  
  return 0;
}