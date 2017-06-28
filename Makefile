# These are the directories that contain everything we need after 'make setup'
# is completed.  We assume that 'matlab' is available on the PATH.
export ROOTPATH := $(shell pwd)
export INCLUDEPATH := $(shell echo $(ROOTPATH))/libraries/include/
export LIBPATH := $(shell echo $(ROOTPATH))/libraries/lib/
export BINPATH := $(shell echo $(ROOTPATH))/libraries/bin/
export JAVAPATH := $(shell echo $(ROOTPATH))/libraries/share/
export DEBUGBINPATH := $(shell echo $(ROOTPATH))/libraries/debug/bin/
export DEBUGINCLUDEPATH := $(shell echo $(ROOTPATH))/libraries/debug/include/
export DEBUGLIBPATH := $(shell echo $(ROOTPATH))/libraries/debug/lib/

# Locate the python bin.
PYTHON_BIN := $(shell which python3.3)
ifndef PYTHON_BIN
  PYTHON_BIN := $(shell which python3)
  ifndef PYTHON_BIN
    PYTHON_BIN := $(shell which python)
  endif
endif
ifdef PYTHON_BIN
# Get the python version.
ifeq ($(shell expr `$(PYTHON_BIN) -c 'import sys; print(sys.version[:3])'` \>= 3.3)	, 1)
  PYTHON_VERSION := 1
endif

# Check if yaml is installed.
YAML_CHECK := $(shell $(PYTHON_BIN) -c 'import sys, yaml;' 2>&1)
ifndef YAML_CHECK
  YAML_INSTALLED := 1
endif

# Check if numpy is installed.
NUMPY_CHECK := $(shell $(PYTHON_BIN) -c 'import sys, numpy;' 2>&1)
ifndef NUMPY_CHECK
  NUMPY_INSTALLED := 1
endif
endif

# Specify the benchmark settings.
CONFIG := config.yaml
BENCHMARKDDIR := benchmark
LOG := False
BLOCK := ""
METHODBLOCK := ""
UPDATE := False
FILES := ""
COPY := False
USER := ""
PASSWORD := ""
BUILD_CORES := 1

# Set the environment variable for the compiled mlpack executables.
export MLPACK_BIN_SRC=methods/mlpack/src/build/
export MLPACK_BIN_DEBUG_SRC=methods/mlpack/src/build/

# Set the environment variable for the the ms_print executable.
export MS_PRINT_BIN=$(shell which ms_print)

# Set the environment variable for the valgrind executable.
export VALGRIND_BIN=$(shell which valgrind)

# Export the path to the FLANN library.
export FLANN_PATH=methods/flann/
# Export the path to the ANN library.
export ANN_PATH=methods/ann/

# Set LD_LIBRARY_PATH correctly.
export LD_LIBRARY_PATH=$(shell echo $(LIBPATH))
# Set PYTHONPATH correctly.
PYVERSION=$(shell python3 -c 'import sys; print("python" + sys.version[0:3])')
export PYTHONPATH=$(shell printenv PYTHONPATH):$(shell echo $(ROOTPATH))/libraries/lib/$(shell echo $(PYVERSION))/dist-packages:$(shell echo $(ROOTPATH))/libraries/lib/$(shell echo $(PYVERSION))/site-packages
# Set MATLABPATH correctly.
export MATLABPATH=$(shell printenv MATLABPATH):$(shell pwd)/methods/matlab

# Color settings.
NO_COLOR=\033[0m
ERROR_COLOR=\033[0;31m
WARN_COLOR=\033[0;33m

.PHONY: help test run memory scripts

help: .check .help
test: .check .test
run: .check .run
memory: .check .check_memory .memory
scripts: .scripts
setup: .check .setup
checks: .check .checks

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
	@echo "  memory [parameters]    Get memory profiling information with the given config."
	@echo "  scripts                Compile any benchmarking scripts."
	@echo "  setup                  Download packages and install into libraries/."
	@echo "  help                   Show this info."
	@echo "  checks                 Run unit tests for benchmarking scripts."
	@echo ""
	@echo "For further information consult the documentation found at \
	http://www.mlpack.org"

.check:
ifndef YAML_INSTALLED
	@echo "$(ERROR_COLOR)[ERROR]$(NO_COLOR) The python 'yaml' module was not \
	found; please install the 'yaml' module to start the benchmark script."
	@exit 1
endif

ifndef PYTHON_BIN
	@echo "$(ERROR_COLOR)[ERROR]$(NO_COLOR) Python not found; please install \
	python to start the benchmark script."
	@exit 1
else
ifndef PYTHON_VERSION
	@echo "$(WARN_COLOR)[WARN]$(NO_COLOR) The benchmark script requires \
	python3.3+ to run all tests properly; however, some modules may still \
	work with older python versions."
endif
endif

ifndef NUMPY_INSTALLED
	@echo "$(ERROR_COLOR)[ERROR]$(NO_COLOR) The python 'numpy' module \
	was not found; please install the 'numpy' module to create the benchmark reports."
	@exit 1
endif

.check_memory:
ifndef VALGRIND_BIN
	@echo "$(ERROR_COLOR)[ERROR]$(NO_COLOR) The valgrind executable \
	was not found; please install valgrind to run the memory benchmark."
	@exit 1
endif

ifndef MS_PRINT_BIN
	@echo "$(ERROR_COLOR)[ERROR]$(NO_COLOR) The Massif 'ms_print' command was \
	not found; please install the massif 'ms_print' command to run the memory benchmark."
	@exit 1
endif

.test:
	$(PYTHON_BIN) $(BENCHMARKDDIR)/test_config.py -c $(CONFIG)

.run:
	$(PYTHON_BIN) $(BENCHMARKDDIR)/run_benchmark.py -c $(CONFIG) -b $(BLOCK) -l $(LOG) -u $(UPDATE) -m $(METHODBLOCK) --f $(FILES) --n $(COPY) -r $(USER) -p $(PASSWORD)

.memory:
	$(PYTHON_BIN) $(BENCHMARKDDIR)/memory_benchmark.py -c $(CONFIG) -b $(BLOCK) -l $(LOG) -u $(UPDATE) -m $(METHODBLOCK)

.scripts:
	# Compile the java files for the weka methods.
	javac -cp "$(JAVAPATH)"weka.jar -d methods/weka methods/weka/src/*.java
	# Compile the ann scripts.
	g++ -O0 -std=c++11 methods/ann/src/allknn.cpp -o methods/ann/allknn -I"$(INCLUDEPATH)" -L"$(LIBPATH)" -lANN -lmlpack -lboost_program_options
	# Compile the FLANN scripts.
	g++ -O0 -std=c++11 methods/flann/src/allknn.cpp -o methods/flann/allknn -I"$(INCLUDEPATH)" -L"$(LIBPATH)" -lmlpack -lboost_program_options -llz4
	# Compile the mlpack scripts.  (Can't do this until ANN is released or a
	# git version of mlpack is used.)
	#cd methods/mlpack/src/ && ./build_scripts.sh

.setup:
	cd libraries/ && ./download_packages.sh && ./install_all.sh $(BUILD_CORES)

.checks:
	$(PYTHON_BIN) tests/tests.py
