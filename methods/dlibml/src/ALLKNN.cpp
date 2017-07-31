#include <dlib/graph_utils.h>
#include <dlib/rand.h>
#include <mlpack/core.hpp>
#include <mlpack/core/util/timers.hpp>

using namespace mlpack;
using namespace std;
using namespace dlib;

// Information about the program itself.
PROGRAM_INFO("K Nearest Neighbors",
    "This program will perform K Nearest Neighbors with the DLib-ml "
    "library.");

// Define our input parameters that this program will take.
PARAM_STRING_IN("reference_file", "File containing the reference dataset.",
    "r", "");
PARAM_INT_IN("k", "Value of K", "k", 0);

int main(int argc, char** argv)
{
  // Parse command line options.
  CLI::ParseCommandLine(argc, argv);

  // Get all the parameters.
  const string referenceFile = CLI::GetParam<string>("reference_file");

  size_t k = CLI::GetParam<int>("k");

  arma::mat referenceData;
  data::Load(referenceFile, referenceData, true);

  Log::Info << "Loaded reference data from '" << referenceFile << "' ("
      << referenceData.n_rows << " x " << referenceData.n_cols << ")." << endl;
  
 
  typedef matrix<double, 0, 1> sample_type; 
  std::vector<sample_type> samples_train;
  std::vector<sample_pair> out;
  
  sample_type m;
  m.set_size(referenceData.n_rows);
  for (size_t i = 0; i < referenceData.n_cols; ++i)
  {
   for (size_t j = 0; j < referenceData.n_rows; ++j)
     m(j) = referenceData(j, i);

    samples_train.push_back(m);
  }

  Timer::Start("Nearest_Neighbors");
  
  find_k_nearest_neighbors(samples_train, squared_euclidean_distance(), 2, out);
  
  Timer::Stop("Nearest_Neighbors");
  
  return 0;
}
