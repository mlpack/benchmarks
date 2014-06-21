#define private protected
#include <shogun/multiclass/GaussianNaiveBayes.h>
#undef private


#include <shogun/features/DenseFeatures.h>
#include <shogun/features/RealFileFeatures.h>
#include <shogun/io/AsciiFile.h>
#include <fstream>

using namespace shogun;

// Define a new GaussianNaiveBayes class with the opportunity to return the probabilities.
class GaussianNaiveBayes : public CGaussianNaiveBayes
{
  public:
    GaussianNaiveBayes(CFeatures* train_examples,
        CLabels* train_labels) : CNativeMulticlassMachine(), m_features(NULL),
    m_min_label(0), m_num_classes(0), m_dim(0), m_means(),
    m_variances(), m_label_prob(), m_rates()

  {
    set_labels(train_labels);
    set_features((CDotFeatures*)train_examples);
  }
    virtual void get_probs(CFeatures* data) {
      if (data)
            set_features(data);

      ASSERT(m_features)
      int32_t num_vectors = m_features->get_num_vectors();
      std::ofstream outfile;
      outfile.open("shogun_probs.csv",std::ios_base::app);
      for (int i=0; i<num_vectors; i++) {
        apply_one(i);
        for (int j=0; j<m_num_classes; j++) {
          outfile << std::to_string(m_rates.vector[j]);
          outfile << ",";
        }
        outfile << "\n";
      }
      outfile.close(); 
    };
};

int main(int argc, char** argv)
{
  init_shogun_with_defaults();

  // Get the input dataset.
  const char* dataset_file = argv[1];

  // Get the labels.
  const char* labels_file = argv[2];

  //Get the test data
  const char* testdata_file = argv[3];

  // Load the input dataset.
  CAsciiFile* dfile = new CAsciiFile(dataset_file);
  SGMatrix<float64_t> dmat = SGMatrix<float64_t>();
  dmat.load(dfile);
  SG_UNREF(dfile);

  // Load the labels
  CAsciiFile* lfile = new CAsciiFile(labels_file);
  SGVector<float64_t> lmat = SGVector<float64_t>();
  lmat.load(lfile);
  SG_UNREF(lfile);

  // Load the test dataset.
  CAsciiFile* tfile = new CAsciiFile(testdata_file);
  SGMatrix<float64_t> tmat = SGMatrix<float64_t>();
  tmat.load(tfile);
  SG_UNREF(tfile);
  
  // Convert the labels.
  CMulticlassLabels* labels = new CMulticlassLabels(lmat);
  SG_REF(labels);

  // Convert the data from the dataset.
  CDenseFeatures<float64_t>* features = new CDenseFeatures<float64_t>(dmat);
  SG_REF(features);

  CFeatures* test_features = new CFeatures(tmat);
  SG_REF(test_features);

  // Create the nbc classifier.
  CGaussianNaiveBayes* ci = new GaussianNaiveBayes(features, labels);
  ci->train();

  // Get the propbs.
  GVector<float64_t> p_test = ci->get_probs(test_features);

  exit_shogun();

  return 0;
}
