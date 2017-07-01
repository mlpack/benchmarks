'''
  @file allknn.py
  @author Marcus Edel

  Class to benchmark the HLearn All K-Nearest-Neighbors method with cover-trees.
'''

import os
import sys
import inspect

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from log import *
from profiler import *

import shlex
import subprocess
import re
import collections

'''
This class implements the All K-Nearest-Neighbor Search benchmark.
'''
class ALLKNN(object):

  '''
  Create the All K-Nearest-Neighbors benchmark instance, show some informations
  and return the instance.

  @param dataset - Input dataset to perform All K-Nearest-Neighbors on.
  @param timeout - The time until the timeout. Default no timeout.
  @param path - Path to the flann executable.
  @param verbose - Display informational messages.
  '''
  def __init__(self, dataset, timeout=0, path=os.environ["HLEARN_PATH"],
        verbose = True):
    self.verbose = verbose
    self.dataset = dataset
    self.path = path
    self.timeout = timeout

  '''
  Destructor to clean up at the end. Use this method to remove created files.
  '''
  def __del__(self):
    Log.Info("Clean up.", self.verbose)
    filelist = ["neighbors_hlearn.csv", "distances_hlearn.csv"]
    for f in filelist:
      if os.path.isfile(f):
        os.remove(f)

  '''
  Perform All K-Nearest-Neighbors. If the method has been successfully completed
  return the elapsed time in seconds.

  @param options - Extra options for the method.
  @return - Elapsed time in seconds or a negative value if the method was not
  successful.
  '''
  def RunMetrics(self, options):
    Log.Info("Perform ALLKNN.", self.verbose)

    # This is not tested since HLearn has not worked in the current benchmarking
    # setup, but, if you are trying to get it to work, this *should* work...
    optionsStr = ""
    if "k" in options:
      optionsStr = "-k " + str(options["k"])
    if "seed" in options:
      optionsStr = optionsStr + " -s " + str(options["seed"])

    # If the dataset contains two files then the second file is the query file.
    # In this case we add this to the command line.
    if len(self.dataset) == 2:
      cmd = shlex.split(self.path + "hlearn-allknn -r " + self.dataset[0] + " -q " +
          self.dataset[1] + " " + optionsStr)
    else:
      cmd = shlex.split(self.path + "hlearn-allknn -r " + self.dataset +
          " " + optionsStr)

    # Run command with the nessecary arguments and return its output as a byte
    # string. We have untrusted input so we disable all shell based features.
    try:
      s = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=False,
          timeout=self.timeout)
    except subprocess.TimeoutExpired as e:
      Log.Warn(str(e))
      return -2
    except Exception as e:
      Log.Fatal("Could not execute command: " + str(cmd))
      return -1

    # Datastructure to store the results.
    metrics = {}

    # Parse data: runtime.
    timer = self.parseTimer(s)

    if timer != -1:
      metrics['Runtime'] = timer.mkShuffleMap + \
                           timer.varshifting_data + \
                           timer.tree_building + \
                           timer.adopting + \
                           timer.sorting_children + \
                           timer.packing_reference_tree + \
                           timer.caching_distances + \
                           timer.computing_parFindNeighborMap + \
                           timer.sorting_results

      metrics['TreeBuilding'] = timer.tree_building + \
                                timer.adopting + \
                                timer.sorting_children + \
                                timer.packing_reference_tree + \
                                timer.caching_distances

      metrics['ComputingNeighbors'] = timer.computing_parFindNeighborMap + \
                                      timer.sorting_results

      Log.Info(("total time: %fs" % (metrics['Runtime'])), self.verbose)

    return metrics

  '''
  Parse the timer data form a given string.

  @param data - String to parse timer data from.
  @return - Namedtuple that contains the timer data or -1 in case of an error.
  '''
  def parseTimer(self, data):
    # Compile the regular expression pattern into a regular expression object to
    # parse the timer data.
    pattern = re.compile(r"""
        .*?mkShuffleMap.*?time=(?P<mkShuffleMap>.*?)s.*?
        .*?varshifting\ data.*?time=(?P<varshifting_data>.*?)s.*?
        .*?building\ tree.*?time=(?P<tree_building>.*?)s.*?
        .*?adopting.*?time=(?P<adopting>.*?)s.*?
        .*?sorting\ children.*?time=(?P<sorting_children>.*?)s.*?
        .*?packing\ reference\ tree.*?time=(?P<packing_reference_tree>.*?)s.*?
        .*?caching\ distances.*?time=(?P<caching_distances>.*?)s.*?
        .*?computing\ parFindNeighborMap.*?time=(?P<computing_parFindNeighborMap>.*?)s.*?
        .*?sorting\ results.*?time=(?P<sorting_results>.*?)s.*?
        .*?outputing\ distance.*?time=(?P<outputing_distance>.*?)s.*?
        .*?outputting\ neighbors.*?time=(?P<outputting_neighbors>.*?)s.*?
        """, re.VERBOSE|re.MULTILINE|re.DOTALL)

    match = pattern.match(data.decode())

    if not match:
      Log.Fatal("Can't parse the data: wrong format")
      return -1
    else:
      # Create a namedtuple and return the timer data.
      timer = collections.namedtuple("timer", ["mkShuffleMap",
                                               "varshifting_data",
                                               "tree_building",
                                               "adopting",
                                               "sorting_children",
                                               "packing_reference_tree",
                                               "caching_distances",
                                               "computing_parFindNeighborMap",
                                               "sorting_results",
                                               "outputing_distance",
                                               "outputting_neighbors"])

      return timer(float(match.group("mkShuffleMap")),
                   float(match.group("varshifting_data")),
                   float(match.group("tree_building")),
                   float(match.group("adopting")),
                   float(match.group("sorting_children")),
                   float(match.group("packing_reference_tree")),
                   float(match.group("caching_distances")),
                   float(match.group("computing_parFindNeighborMap")),
                   float(match.group("sorting_results")),
                   float(match.group("outputing_distance")),
                   float(match.group("outputting_neighbors")))
