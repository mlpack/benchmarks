# Locate the python bin.
PYTHON_BIN := $(shell which python3.2)
ifndef PYTHON_BIN
  PYTHON_BIN := $(shell which python3)
  ifndef PYTHON_BIN
    PYTHON_BIN := $(shell which python)
  endif
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
METHODBLOCK:=""
UPDATE:=False

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
ERROR_COLOR=\033[0;31m
WARN_COLOR=\033[0;33m

.PHONY: help test run memory scripts reports

help: .check .help
test: .check .test
run: .check .run
memory: .check .memory
reports: .check .reports
scripts: .scripts

.help:
	@echo "Benchmark-Script"
	@echo ""
	@echo "   This script will test various methods with different data sets."
	@echo ""
	@echo "   For example, the following will run all scripts and methods defined"
	@echo "   in the config.yaml file and the results are shown on the console:"
	@echo ""
	@echo "   $$ make run CONFIG=config LOG=False"
	@echo ""
	@echo "   Usage: make [option] [parameters]"
	@echo ""
	@echo "Parameters:"
	@echo "  CONFIG [string]        The path to the configuration file to perform the benchmark on."
	@echo "                         Default '$(CONFIG)'."
	@echo "  BLOCK [string]         Run only the specified blocks defined in the configuration file."
	@echo "                         Default run all blocks."
	@echo "  LOG [boolean]          If set, the reports will be saved in the database."
	@echo "                         Default '$(LOG)'."
	@echo "  UPDATE [boolean]       If set, the latest reports in the database are updated."
	@echo "                         Default '$(UPDATE)'."
	@echo "  METHODBLOCK [string]   Run only the specified methods defined in the configuration file."
	@echo "                         Default run all methods."
	@echo ""
	@echo "Options:"
	@echo "  test [parameters]      Test the configuration file. Check for correct"
	@echo "                         syntax and then try to open files referred in the"
	@echo "                         configuration file."
	@echo "  run [parameters]       Perform the benchmark with the given config."
	@echo "  memory [parameters]    Get memory profiling information with the given config"
	@echo "  scripts                Compile the java files for the weka methods."
	@echo "  reports [parameters]   Create the reports."
	@echo "  help                   Show this info."
	@echo ""
	@echo "For further information consult the documentation found at \
	http://www.mlpack.org"

.check:
ifndef YAML_INSTALLED
	@echo "$(ERROR_COLOR)[ERROR]$(NO_COLOR) The python 'yaml' module was not \
	found; please install the yaml module to start the benchmark script."
	@exit 1
endif

ifndef PYTHON_BIN
	@echo "$(ERROR_COLOR)[ERROR]$(NO_COLOR) Python not found; please install \
	python to start the benchmark script."
	@exit 1
else
ifndef PYTHON_VERSION
	@echo "$(WARN_COLOR)[WARN]$(NO_COLOR) The benchmark script requires \
	python3.2+ to run all tests properly; however, some modules may still \
	work with older python versions."
endif
endif

.test:
	$(PYTHON_BIN) $(BENCHMARKDDIR)/test_config.py -c $(CONFIG)

.run:
	$(PYTHON_BIN) $(BENCHMARKDDIR)/run_benchmark.py -c $(CONFIG) -b $(BLOCK) -l $(LOG) -u $(UPDATE) -m $(METHODBLOCK)

.memory:
	$(PYTHON_BIN) $(BENCHMARKDDIR)/memory_benchmark.py -c $(CONFIG) -b $(BLOCK) -l $(LOG) -u $(UPDATE) -m $(METHODBLOCK)

.reports:
	$(PYTHON_BIN) $(BENCHMARKDDIR)/make_reports.py -c $(CONFIG)

.scripts:
	# Compile the java files for the weka methods.
	javac -cp $(shell echo $(WEKA_CLASSPATH)) -d methods/weka methods/weka/src/*.java
	# Compile the shogun K-Means (with initial centroids) Clustering method.
	g++ -O0 methods/shogun/src/kmeans.cpp -o methods/shogun/kmeans -I$(SHOGUN_PATH)/include -L$(SHOGUN_PATH)/lib -lshogun
