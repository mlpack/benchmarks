#include <dlib/clustering.h>
#include <dlib/rand.h>
#include <mlpack/core.hpp>
#include <mlpack/core/util/timers.hpp>

using namespace mlpack;
using namespace std;
using namespace dlib;

// Information about the program itself.
PROGRAM_INFO("KMEANS Clustering",
    "This program will perform KMEANS clustering with the DLib-ml "
    "library.");

// Define our input parameters that this program will take.
PARAM_STRING_IN("reference_file", "File containing the reference dataset.",
    "r", "");
PARAM_INT_IN("k", "Value of K", "k", 0);
PARAM_STRING_IN("query_file", "File containing query points (optional).", "q", "");

int main(int argc, char** argv)
{
  // Parse command line options.
  CLI::ParseCommandLine(argc, argv);

  // Get all the parameters.
  const string referenceFile = CLI::GetParam<string>("reference_file");
  const string queryFile = CLI::GetParam<string>("query_file");

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
  
  typedef matrix<double, 0, 1> sample_type; 
  typedef radial_basis_kernel<sample_type> kernel_type;

  kcentroid<kernel_type> kc(kernel_type(0.1), 0.01, 8);
  kkmeans<kernel_type> test(kc);

  std::vector<sample_type> samples;
  std::vector<sample_type> initial_centers;
  
  sample_type m;
  m.set_size(referenceData.n_rows);
  for (size_t i = 0; i < referenceData.n_cols; ++i)
  {
   for (size_t j = 0; j < referenceData.n_rows; ++j)
     m(j) = referenceData(j, i);

    samples.push_back(m);
  }

  if (queryFile != "")
  {
   sample_type centers;
   centers.set_size(referenceData.n_rows);

   for (size_t i = 0; i < queryData.n_cols; ++i)
   {
   for (size_t j = 0; j < queryData.n_rows; ++j)
     centers(j) = queryData(j, i);

    initial_centers.push_back(centers);
   }

  }

  else
  pick_initial_centers(k, initial_centers, samples, test.get_kernel());

  test.set_number_of_centers(k);
  Timer::Start("clustering");
  
  test.train(samples,initial_centers);
  for(size_t i = 0; i< samples.size();i++)
  {
   size_t assignment = test(samples[i]);
  }  
  Timer::Stop("clustering");
  
  return 0;
}


