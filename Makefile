PYTHON_BIN := $(shell which python3.3)
PYTHON_VERSION := $(shell expr `$(PYTHON_BIN) -c 'import sys; print(sys.version[:3])'` \>= 2.7)
YAML_INSTALLED := $(shell $(PYTHON_BIN) -c 'import sys, yaml;' 2>&1)

CONFIG := config.yaml
BENCHMARKDDIR := benchmark
LOG:=False
BLOCK:=""

# Specify the path for the libraries.
export MLPACK_BIN=/usr/local/bin/
export MLPACK_BIN_DEBUG=/usr/local/bin/
export MATLAB_BIN=/opt/matlab/bin/
export MATLABPATH=methods/matlab/
export WEKA_CLASSPATH=".:/opt/weka/weka-3-6-9:/opt/weka/weka-3-6-9/weka.jar"
export SHOGUN_PATH=/opt/shogun/shogun-2.1.0-mod
export PYTHONPATH=/opt/scikit-learn/scikit-learn-0.13.1/lib/python3.3/site-packages/:/opt/mlpy/mlpy-3.5.0/lib/python3.3/site-packages/:/opt/shogun/shogun-2.1.0/lib/python3.3/dist-packages/
export LD_LIBRARY_PATH=/opt/shogun/shogun-2.1.0/lib/
export MS_PRINT_BIN=/usr/bin/ms_print
export VALGRIND_BIN=/usr/bin/valgrind

ifeq ($(PYTHON_VERSION), 0)
	$(error Python version 2.7 required which was not found)
endif

# This is empty unless there was a problem.
ifdef YAML_INSTALLED
	$(error Python 'yaml' module was not found)
endif

.PHONY: help test run memory scripts reports

help:
	@echo "$(YAML_INSTALLED)"
	@echo "Usage: make [option] [CONFIG=..]"
	@echo "options:"
	@echo "  help               Show this info."
	@echo "  test [CONFIG]      Test the configuration file. Check for correct"
	@echo "                     syntax and then try to open files referred in the"
	@echo "                     configuration. Default ''."
	@echo "  run [CONFIG]       Perform the benchmark with the given config."
	@echo "                     Default '$(CONFIG)'."
	@echo "  memory [CONFIG]    Get memory profiling information with the given "
	@echo "                     config. Default '$(CONFIG)'."
	@echo "  scripts            Compile the java files for the weka methods."
	@echo "  reports [CONFIG]   Create the reports. Default '$(CONFIG)'."

test:
	$(PYTHON_BIN) $(BENCHMARKDDIR)/test_config.py -c $(CONFIG)

run:
	$(PYTHON_BIN) $(BENCHMARKDDIR)/run_benchmark.py -c $(CONFIG) -b $(BLOCK) -l $(LOG)

memory:
	$(PYTHON_BIN) $(BENCHMARKDDIR)/memory_benchmark.py -c $(CONFIG)

reports:
	$(PYTHON_BIN) $(BENCHMARKDDIR)/make_reports.py -c $(CONFIG)

scripts:
	# Compile the java files for the weka methods.
	javac -cp $(shell echo $(WEKA_CLASSPATH)) -d methods/weka methods/weka/src/*.java
	# Compile the shogun K-Means (with initial centroids) Clustering method.
	g++ -O0 methods/shogun/src/kmeans.cpp -o methods/shogun/kmeans -I$(SHOGUN_PATH)/include -L$(SHOGUN_PATH)/lib -lshogun
