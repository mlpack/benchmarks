'''
  @file kmeans.py
  @author Erich Schubert
  @author Marcus Edel -- original weka version

  Class to benchmark the ELKI K-Means Clustering method.
'''

import os, sys, inspect, shlex, subprocess, re

# Import the util path, this method even works if the path contains symlinks to
# modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../util")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from util import *

'''
This class implements the K-Means Clustering benchmark.
'''
class ELKI_KMEANS(object):
  def __init__(self, method_param, run_param):
    # Assemble run command.
    if "datasets" in method_param:
      dataset = method_param["datasets"]

    centroids = None
    if len(dataset) == 2:
        centroids = load_dataset(dataset[1], ["csv"])[0]
        centroids = ";".join(map(lambda x:",".join(map(str, x)), centroids))

    self.cmd = ["java", "-jar", run_param["java_path"] + "elki.jar", "cli",
      "-time", "-dbc.in", str(dataset[0]), "-algorithm",
      "clustering.kmeans.KMeansSort", "-resulthandler", "DiscardResultHandler"]
    if centroids:
        self.cmd += ["-kmeans.initialization", "PredefinedInitialMeans",
            "-kmeans.means", centroids]
    else:
        self.cmd += ["-kmeans.initialization", "KMeansPlusPlusInitialMeans"]
    if "clusters" in method_param:
      self.cmd += ["-kmeans.k", str(method_param["clusters"])]


    self.info = "ELKI_KMEANS (" + str(self.cmd) + ")"
    self.timeout = run_param["timeout"]
    self.output = None

  def __str__(self):
    return self.info

  def metric(self):
    try:
      self.output = subprocess.check_output(self.cmd, stderr=subprocess.STDOUT,
        shell=False, timeout=self.timeout)
    except subprocess.TimeoutExpired as e:
      raise Exception("method timeout")
    except Exception as e:
      subprocess_exception(e, self.output)

    metric = {}
    pattern = re.compile(r""".*?algorithm[^\s]*?runtime:\s+(?P<total_time>\d+)\s*ms.*?""", re.VERBOSE|re.MULTILINE|re.DOTALL)
    match = pattern.match(self.output.decode())

    if match.group("total_time").count(".") == 1:
      metric["runtime"] = float(match.group("total_time")) / 1000.
    else:
      metric["runtime"] = float(match.group("total_time").replace(",", ".")) / 1000.

    return metric
