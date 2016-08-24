/**
 * @file allknn.cpp
 * @author Marcus Edel
 *
 * Code to benchmark the flann All K-Nearest-Neighbors method with kd-trees.
 */

#include <mlpack/core.hpp>
#include <mlpack/core/util/timers.hpp>
#include <flann/flann.hpp>

using namespace mlpack;
using namespace flann;
using namespace std;

// Information about the program itself.
PROGRAM_INFO("All K-Nearest-Neighbors",
    "This program will calculate the all k-nearest-neighbors with the flann "
    "library.");

// Define our input parameters that this program will take.
PARAM_STRING_IN("reference_file", "File containing the reference dataset.",
    "r", "");
PARAM_INT_IN("k", "Number of nearest neighbors to find.", "k", 0);
PARAM_STRING_IN("query_file", "File containing query points (optional).", "q", "");
PARAM_STRING_OUT("distances_file", "File to output distances into.", "d");
PARAM_STRING_OUT("neighbors_file", "File to output neighbors into.", "n");
PARAM_INT_IN("leaf_size", "Leaf size for tree building.", "l", 20);
PARAM_INT_IN("seed", "Random seed (if 0, std::time(NULL) is used).", "s", 0);
PARAM_DOUBLE_IN("epsilon", "If specified, will do approximate nearest neighbor "
    "search with given relative error.", "e", 0);

int main(int argc, char** argv)
{
  // Parse command line options.
  CLI::ParseCommandLine(argc, argv);

  // Get all the parameters.
  const string referenceFile = CLI::GetParam<string>("reference_file");
  const string queryFile = CLI::GetParam<string>("query_file");

  int lsInt = CLI::GetParam<int>("leaf_size");

  size_t k = CLI::GetParam<int>("k");
  bool monoSearch = false;

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

  // Sanity check on k value: must be greater than 0, must be less than the
  // number of reference points.
  if (k > referenceData.n_cols)
  {
    Log::Fatal << "Invalid k: " << k << "; must be greater than 0 and less ";
    Log::Fatal << "than or equal to the number of reference points (";
    Log::Fatal << referenceData.n_cols << ")." << endl;
  }

  // Sanity check on epsilon.
  const double epsilon = CLI::GetParam<double>("epsilon");
  if (epsilon < 0)
    Log::Fatal << "Invalid epsilon: " << epsilon << ".  Must be "
        "non-negative. " << endl;

  // Sanity check on leaf size.
  if (lsInt < 0)
  {
    Log::Fatal << "Invalid leaf size: " << lsInt << ".  Must be greater "
        "than or equal to 0." << endl;
  }
  size_t leafSize = lsInt;

  flann::Matrix<double> dataset = flann::Matrix<double>(
      referenceData.memptr(), referenceData.n_cols, referenceData.n_rows);
  flann::Matrix<double> query;
  if (queryFile != "")
  {
    query = flann::Matrix<double>(queryData.memptr(), queryData.n_cols,
        queryData.n_rows);
  }
  else
  {
    monoSearch = true;
    ++k;
    query = flann::Matrix<double>(referenceData.memptr(),
        referenceData.n_cols, referenceData.n_rows);
  }

  Matrix<int> indices(new int[query.rows*k], query.rows, k);
  Matrix<double> dists(new double[query.rows*k], query.rows, k);

  arma::mat distances(monoSearch ? k - 1 : k, query.rows);
  arma::Mat<size_t> neighbors(monoSearch ? k - 1 : k, query.rows);

  Timer::Start("tree_building");

  // Perform All K-Nearest-Neighbors.
  Index<L2<double> > index(dataset, flann::KDTreeSingleIndexParams(leafSize));
  index.buildIndex();

  Timer::Stop("tree_building");

  Timer::Start("computing_neighbors");

  index.knnSearch(query, indices, dists, k, flann::SearchParams(0, epsilon));

  if (monoSearch)
  {
    for (size_t c = 0; c < query.rows ; c++)
      for (size_t r = 1; r < k; r++)
      {
        distances(r - 1, c) = sqrt(dists[c][r]);
        neighbors(r - 1, c) = indices[c][r];
      }
  }
  else
  {
    for (size_t c = 0; c < query.rows ; c++)
      for (size_t r = 0; r < k; r++)
      {
        distances(r, c) = sqrt(dists[c][r]);
        neighbors(r, c) = indices[c][r];
      }
  }

  Timer::Stop("computing_neighbors");

  // Save output, if desired.
  if (CLI::HasParam("distances_file"))
    data::Save(CLI::GetParam<string>("distances_file"), distances);

  if (CLI::HasParam("neighbors_file"))
    data::Save(CLI::GetParam<string>("neighbors_file"), neighbors);

  delete[] indices.ptr();
  delete[] dists.ptr();

  return 0;
}
