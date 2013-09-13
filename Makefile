# Locate the python bin.
PYTHON_BIN := $(shell which python3.2)
ifndef PYTHON_BIN
  PYTHON_BIN := $(shell which python)
endif

ifdef PYTHON_BIN
# Get the python version.
ifeq ($(shell expr `$(PYTHON_BIN) -c 'import sys; print(sys.version[:3])'` \>= 3.2)	, 1)
  PYTHON_VERSION := 1
endif

# Check if yaml is installed.
YAML_CHECK := $(shell $(PYTHON_BIN) -c 'import sys, yaml;' 2>&1)
ifndef YAML_CHECK
  YAML_INSTALLED := 1
endif
endif

# Specify the benchmark settings.
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

# Color settings.
NO_COLOR=\033[0m
ERROR_COLOR=\x1b[31;01m
WARN_COLOR=\x1b[33;01m

.PHONY: help test run memory scripts reports

help: .check .help
test: .check .test
run: .check .run
memory: .check .memory
reports: .check .reports
scripts: .scripts

.help:
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

.check:
ifndef YAML_INSTALLED
	@echo "$(ERROR_COLOR)[ERROR]$(NO_COLOR) The python 'yaml' module was not \
	found please install the yaml module to start the benchmark script."
	@exit 1
endif

ifndef PYTHON_BIN
	@echo "$(ERROR_COLOR)[ERROR]$(NO_COLOR) Python not found please install \
	python to start the benchmark script."
	@exit 1
else
ifndef PYTHON_VERSION
	@echo "$(WARN_COLOR)[WARN]$(NO_COLOR) The benchmark script requires \
	python3.2+ to run properly."
endif
endif

.test:
	$(PYTHON_BIN) $(BENCHMARKDDIR)/test_config.py -c $(CONFIG)

.run:
	$(PYTHON_BIN) $(BENCHMARKDDIR)/run_benchmark.py -c $(CONFIG) -b $(BLOCK) -l $(LOG)

.memory:
	$(PYTHON_BIN) $(BENCHMARKDDIR)/memory_benchmark.py -c $(CONFIG) -b $(BLOCK) -l $(LOG)

.reports:
	$(PYTHON_BIN) $(BENCHMARKDDIR)/make_reports.py -c $(CONFIG)

.scripts:
	# Compile the java files for the weka methods.
	javac -cp $(shell echo $(WEKA_CLASSPATH)) -d methods/weka methods/weka/src/*.java
	# Compile the shogun K-Means (with initial centroids) Clustering method.
	g++ -O0 methods/shogun/src/kmeans.cpp -o methods/shogun/kmeans -I$(SHOGUN_PATH)/include -L$(SHOGUN_PATH)/lib -lshogun
