'''
  @file pca.py
  @author Erich Schubert
  @author Marcus Edel -- original weka version

  Class to benchmark the ELKI Principal Components Analysis method.

  TODO: the measured time currently includes the time to parse the data.
  Since PCA is not a streaming filter, we could get the actually processing time seperately.
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
This class implements the Principal Components Analysis benchmark.
'''
class ELKI_PCA(object):
  def __init__(self, method_param, run_param):
    # Assemble run command.
    if "datasets" in method_param:
      dataset = method_param["datasets"]

    self.cmd = ["java", "-jar", run_param["java_path"] + "elki.jar", "cli", "-time", "-dbc.in",
      dataset[0], "-algorithm", "NullAlgorithm", "-resulthandler",
      "DiscardResultHandler"] + self.process_options(method_param)

    self.info = "ELKI_PCA (" + str(self.cmd) + ")"
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
    pattern = re.compile(r""".*?datasource[^\s]*\.load:\s*(?P<total_time>\d+)\s*ms.*?""", re.VERBOSE|re.MULTILINE|re.DOTALL)
    match = pattern.match(self.output.decode())
    if match.group("total_time").count(".") == 1:
      metric["runtime"] =  float(match.group("total_time")) / 1000.
    else:
      metric["runtime"] = float(match.group("total_time").replace(",", ".")) / 1000.
    return metric

  def process_options(self, method_param):
    opts = []
    if "whiten" in method_param:
      opts += ["-dbc.filter", "normalization.columnwise.AttributeWiseVarianceNormalization,transform.GlobalPrincipalComponentAnalysisTransform"]
      method_param["whiten"]
    else:
      opts += ["-dbc.filter", "transform.GlobalPrincipalComponentAnalysisTransform"]
    if "new_dimensionality" in method_param:
      opts += ["-globalpca.filter", "FirstNEigenPairFilter", "-pca.filter.n", str(method_param["new_dimensionality"])]

    return opts
