#include <dlib/clustering.h>
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
PARAM_STRING_IN("centroids_file", "File containing centroids points (optional).", "c", "");

int main(int argc, char** argv)
{
  // Parse command line options.
  CLI::ParseCommandLine(argc, argv);

  // Get all the parameters.
  const string referenceFile = CLI::GetParam<string>("reference_file");
  const string centroidsFile = CLI::GetParam<string>("centroids_file");

  size_t k = CLI::GetParam<int>("k");

  arma::mat referenceData;
  arma::mat centroidsData; // So it doesn't go out of scope.
  data::Load(referenceFile, referenceData, true);

  Log::Info << "Loaded reference data from '" << referenceFile << "' ("
      << referenceData.n_rows << " x " << referenceData.n_cols << ")." << endl;
  
  if (centroidsFile != "")
  {
    data::Load(centroidsFile, centroidsData, true);
    Log::Info << "Loaded centroids data from '" << centroidsFile << "' ("
        << centroidsData.n_rows << " x " << centroidsData.n_cols << ")." << endl;
  }
  
  typedef matrix<double, 0, 1> sample_type; 
  typedef radial_basis_kernel<sample_type> kernel_type;


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

  if (centroidsFile != "")
  {
    sample_type centers;
    centers.set_size(referenceData.n_rows);

    for (size_t i = 0; i < centroidsData.n_cols; ++i)
    {
      for (size_t j = 0; j < centroidsData.n_rows; ++j)
        centers(j) = centroidsData(j, i);

      initial_centers.push_back(centers);
    }

  }

  else
    pick_initial_centers(k, initial_centers, samples, linear_kernel<sample_type>());


  arma::mat assignments(1, samples.size());

  Timer::Start("clustering");
  
  find_clusters_using_kmeans(samples, initial_centers);

  for(size_t i = 0; i < samples.size(); i++)
  {
    assignments(i) = nearest_center(initial_centers, samples[i]);
  } 
  
  Timer::Stop("clustering");

  data::Save("assignments.csv", assignments);

  return 0;
}


