#include <dlib/svm_threaded.h>
#include <dlib/rand.h>
#include <mlpack/core.hpp>
#include <mlpack/core/util/timers.hpp>
#include <string>

using namespace mlpack;
using namespace std;
using namespace dlib;

// Information about the program itself.
PROGRAM_INFO("Support Vector Machines",
    "This program will perform SVM with the DLib-ml library");

// Define our input parameters that this program will take.
PARAM_STRING_IN("training_file", "File containing the training dataset.",
    "t", "");
PARAM_STRING_IN("test_file", "File containing the test dataset.",
    "T", "");
PARAM_STRING_IN("kernel", "Name of the kernel to be used.", "k", "");
PARAM_DOUBLE_IN("C", "Bandwidth", "c", 0);
PARAM_DOUBLE_IN("g", "Coef", "g", 0);
PARAM_DOUBLE_IN("d", "Degree", "d", 0);

int main(int argc, char** argv)
{
  // Parse command line options.
  CLI::ParseCommandLine(argc, argv);

  // Get all the parameters.
  const string trainFile = CLI::GetParam<string>("training_file");
  const string testFile = CLI::GetParam<string>("test_file");
  
  const string kernel = CLI::GetParam<string>("k");
  size_t c = CLI::GetParam<double>("c");
  size_t g = CLI::GetParam<double>("g");
  size_t d = CLI::GetParam<double>("d");

  arma::mat trainData;
  arma::mat testData; // So it doesn't go out of scope.

  data::Load(trainFile, trainData, true);

  Log::Info << "Loaded train data from '" << trainFile << "' ("
      << trainData.n_rows << " x " << trainData.n_cols << ")." << endl;

  data::Load(testFile, testData, true);

  Log::Info << "Loaded test data from '" << testFile << "' ("
      << testData.n_rows << " x " << testData.n_cols << ")." << endl;
                                                                                                                             
  typedef matrix<double, 0, 1> sample_type;

  std::vector<sample_type> train;
  std::vector<sample_type> test;
  std::vector<double> labels;

  typedef one_vs_one_trainer<any_trainer<sample_type> > ovo_trainer;
  ovo_trainer trainer;

  typedef polynomial_kernel<sample_type> poly_kernel;
  typedef radial_basis_kernel<sample_type> rbf_kernel;

  krr_trainer<rbf_kernel> rbf_trainer;
  svm_nu_trainer<poly_kernel> poly_trainer;
  if (kernel.compare("polynomial") == 0)
  { 
     poly_trainer.set_kernel(poly_kernel(c, g, d));
     trainer.set_trainer(poly_trainer, 1, 2);
  }
  else if (kernel.compare("rbf") == 0)
  {  
    rbf_trainer.set_kernel(rbf_kernel(c));
    trainer.set_trainer(rbf_trainer);
  }

  sample_type m;
  m.set_size(trainData.n_rows);
  for (size_t i = 0; i < trainData.n_cols; ++i)
  {
    for (size_t j = 0; j < trainData.n_rows - 1; ++j)
      m(j) = trainData(j, i);

    train.push_back(m);
  }
  sample_type m2;
  m2.set_size(1);
  for (size_t j = 0; j < trainData.n_cols; ++j)
  {
    labels.push_back(trainData(trainData.n_rows - 1, j));
  }

  sample_type te;
  te.set_size(testData.n_rows);

                                                                                                                             
  for (size_t i = 0; i < testData.n_cols; ++i)
  {
    for (size_t j = 0; j < testData.n_rows; ++j)
      te(j) = testData(j, i);

    test.push_back(te);
  }

  Timer::Start("runtime");

  one_vs_one_decision_function<ovo_trainer> df = trainer.train(train, labels);
  arma::mat predictions(1, test.size());

  for(size_t i = 0; i < test.size(); i++)
  {
    predictions(i) = df(test[i]);
  }

  Timer::Stop("runtime");

  data::Save("predictions.csv", predictions);

}

