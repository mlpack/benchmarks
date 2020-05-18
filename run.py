'''
  @file run.py
  @author Marcus Edel

  Perform the benchmark.
'''

import os, sys, inspect, argparse, yaml, logging

# Import the util path, this method even works if the path contains
# symlinks to modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], 'util')))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *
from memory_profiler import memory_usage

def run(config, library, methods, loglevel):
  # Configure logging.
  if loglevel and loglevel.upper() == "CRITICAL":
    logginglevel = logging.CRITICAL
  elif loglevel and loglevel.upper() == "ERROR":
    logginglevel = logging.ERROR
  elif loglevel and loglevel.upper() == "WARNING":
    logginglevel = logging.WARNING
  elif loglevel and loglevel.upper() == "DEBUG":
    logginglevel = logging.DEBUG
  else:
    logginglevel = logging.INFO

  logging.basicConfig(level=logginglevel, format='[%(levelname)s] %(message)s')

  stream = open("base.yaml", "r")
  base_param = list(yaml.load_all(stream))[0]

  stream = open("driver.yaml", "r")
  driver_param = list(yaml.load_all(stream))[0]

  # Configure output driver.
  if "output_driver" in driver_param:
    module = Loader.ImportModuleFromPath(driver_param["output_driver"])
    driver = getattr(module, "Driver")(driver_param)

  stream = open(config, "r")
  method_config = yaml.load_all(stream)
  for method in method_config:
    name, values = method.popitem()

    # Skip unspecified libraries, unless the user didn't specify any.
    if library is not None and values["library"].lower() != library.lower():
      continue

    # Skip unspecified methods, unless the user didn't specify any.
    if methods is not None and values["method"].lower() != methods.lower():
      continue

    values["param"] = param_extension(values["param"])

    for method_param in values["param"]:
      method_param.pop("options")

      for dataset in values["datasets"]:
        method_param["datasets"] = \
          dataset if isinstance(dataset, (list,)) else [dataset]

        if "metric" in values["run"]:
          logging.info('Script: %s' % (values["script"]))

          module = Loader.ImportModuleFromPath(values["script"])
          method_call = getattr(module, name)

          try:
            @timeout_decorator.timeout(base_param["timeout"], use_signals=True)
            def run_timeout_wrapper():
              instance = method_call(method_param, base_param)
              logging.info('Run: %s' % (str(instance)))

              # Run the metric method.
              mem_use, result = memory_usage(instance.metric,
                                             interval=1e-3,
                                             include_children=True,
                                             max_usage=True, 
                                             retval=True,
                                             backend="psutil")
              result["memory"] = str(format(mem_use, ".2f")) + "MB"
              logging.info('Metric: %s' % (str(result)))

              # Pass the result to the driver.
              if driver:
                driver.update(values["library"], values["method"],
                  method_param["datasets"], method_param, base_param, result)

              if len(result.keys()) <= 0:
                logging.error('No metric results.')

            run_timeout_wrapper()
          except timeout_decorator.TimeoutError as e:
            logging.warning('Timeout: %s' % (str(e)))
          except Exception as e:
            logging.error('Exception: %s' % (str(e)))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description="""Perform the benchmark with the given config.""")
  parser.add_argument(
    '-c','--config', help='Configuration file name.', required=True)
  parser.add_argument('-l','--lib',
    help='Run only the specified library scripts.', required=False)
  parser.add_argument('-m','--methods',
    help="""Run only the specified methods.""", required=False)
  parser.add_argument('-s','--save',
    help='Save the results.', required=False)
  parser.add_argument('-o','--loglevel',
    help='Loglevel [CRITICAL, ERROR, WARNING, INFO, DEBUG, NONE].',
    required=False)

  args = parser.parse_args()

  if args:
    run(args.config, args.lib, args.methods, args.loglevel)
