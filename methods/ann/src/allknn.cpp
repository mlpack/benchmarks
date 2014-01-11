/**
 * @file allknn.cpp
 * @author Marcus Edel
 *
 * Code to benchmark the ann All K-Nearest-Neighbors method with kd-trees.
 */

#include <mlpack/core.hpp>
#include <mlpack/core/util/timers.hpp>
#include <ANN/ANN.h>

using namespace mlpack;
using namespace std;

// Information about the program itself.
PROGRAM_INFO("All K-Nearest-Neighbors",
    "This program will calculate the all k-nearest-neighbors with the ann "
    "library.");

// Define our input parameters that this program will take.
PARAM_STRING_REQ("reference_file", "File containing the reference dataset.",
    "r");
PARAM_INT_REQ("k", "Number of nearest neighbors to find.", "k");
PARAM_STRING("query_file", "File containing query points (optional).", "q", "");
PARAM_INT("leaf_size", "Leaf size for tree building.", "l", 20);


int main(int argc, char **argv)
{
  // Parse command line options.
  CLI::ParseCommandLine(argc, argv);

  // Get all the parameters.
  const string referenceFile = CLI::GetParam<string>("reference_file");
  const string queryFile = CLI::GetParam<string>("query_file");

  int lsInt = CLI::GetParam<int>("leaf_size");

  size_t k = CLI::GetParam<int>("k");

  arma::mat referenceData;
  arma::mat queryData; // So it doesn't go out of scope.
  data::Load(referenceFile, referenceData, true);

  Log::Info << "Loaded reference data from '" << referenceFile << "' ("
      << referenceData.n_rows << " x " << referenceData.n_cols << ")." << endl;

  if (queryFile != "")
  {
    data::Load(queryFile, queryData, true);
    Log::Info << "Loaded query data from '" << queryFile << "' ("
        << queryData.n_rows << " x " << queryData.n_cols << ")." << endl;
  }
  else
  {
    queryData = referenceData;
  }

  // Sanity check on k value: must be greater than 0, must be less than the
  // number of reference points.
  if (k > referenceData.n_cols)
  {
    Log::Fatal << "Invalid k: " << k << "; must be greater than 0 and less ";
    Log::Fatal << "than or equal to the number of reference points (";
    Log::Fatal << referenceData.n_cols << ")." << endl;
  }

  // Sanity check on leaf size.
  if (lsInt < 0)
  {
    Log::Fatal << "Invalid leaf size: " << lsInt << ".  Must be greater "
        "than or equal to 0." << endl;
  }

  size_t leafSize = lsInt;
  size_t maxPts = referenceData.n_elem;
  size_t dim = referenceData.n_rows;

  ANNidxArray nnIdx = new ANNidx[k];
  ANNdistArray dists = new ANNdist[k];
  ANNpointArray dataPts = annAllocPts(maxPts, dim);

  for (int i = 0; i < referenceData.n_cols; ++i)
  {
    for (int j = 0; j < referenceData.n_rows; ++j)
    {
      dataPts[i][j] = referenceData(j,i);
    }
  }

  Timer::Start("knn_time");

  ANNkd_tree*  kdTree = new ANNkd_tree(dataPts, maxPts, dim, lsInt);

  arma::vec queryPoint;
  for (int i = 0; i < queryData.n_cols; ++i)
  {
    queryPoint = queryData.col(i);
    kdTree->annkSearch(queryPoint.memptr(), k, nnIdx,  dists, 0);

    for (int j = 0; j < k; j++) 
    {     
      dists[j] = sqrt(dists[j]);
    }
  }

  Timer::Stop("knn_time");

  delete [] nnIdx;
  delete [] dists;
  delete kdTree;
  annClose();
  return 0;
}
