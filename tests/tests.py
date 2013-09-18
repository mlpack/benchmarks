import unittest

testmodules = [
'benchmark_allkfn',
'benchmark_allknn',
'benchmark_allkrann',
'benchmark_det',
'benchmark_emst',
'benchmark_fastmks',
'benchmark_gmm',
'benchmark_hmm_generate',
'benchmark_hmm_loglik',
'benchmark_hmm_train',
'benchmark_hmm_viterbi',
'benchmark_ica',
'benchmark_kernel_pca',
'benchmark_kmeans',
'benchmark_lars',
'benchmark_linear_regression',
'benchmark_local_coordinate_coding',
'benchmark_lsh',
'benchmark_nbc',
'benchmark_nca',
'benchmark_nmf',
'benchmark_pca',
'benchmark_range_search',
'benchmark_sparse_coding'
]

suite = unittest.TestSuite()

for t in testmodules:
  try:
    mod = __import__(t, globals(), locals(), ['suite'])
    suitefn = getattr(mod, 'suite')
    suite.addTest(suitefn())
  except (ImportError, AttributeError):
    suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))

unittest.TextTestRunner().run(suite)
