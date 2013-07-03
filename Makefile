PYTHON_BIN := $(shell which python)
PYTHON_VERSION := $(shell expr `$(PYTHON_BIN) -c 'import sys; print sys.version[:3]'` \>= 2.7)
YAML_INSTALLED := $(shell $(PYTHON_BIN) -c 'import sys, yaml;' 2>&1)

CONFIG := config.yaml
BENCHMARKDDIR := benchmark

# Export matlab path to execute matlab file in the methods directory.
export MATLABPATH = methods/matlab/

ifeq ($(PYTHON_VERSION), 0)
  $(error Python version 2.7 required which was not found)
endif

# This is empty unless there was a problem.
ifdef YAML_INSTALLED
  $(error Python 'yaml' module was not found)
endif

.PHONY: help test run memory

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

test:
	$(PYTHON_BIN) $(BENCHMARKDDIR)/test_config.py -c $(CONFIG)

run:
	$(PYTHON_BIN) $(BENCHMARKDDIR)/run_benchmark.py -c $(CONFIG)

memory:
	$(PYTHON_BIN) $(BENCHMARKDDIR)/memory_benchmark.py -c $(CONFIG)

