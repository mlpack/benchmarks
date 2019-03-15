'''
  @file text.py
  @author Marcus Edel

  Text driver.
'''

import os.path

'''
Text driver class to write the output to a text file.
'''
class Driver(object):
  def __init__(self, param):
    self.build = 1
    self.file = param["text_file"]

    self.latest_build()

  def latest_build(self):
    if os.path.isfile(self.file):
      with open(self.file, 'r') as f:
        lines = f.read().splitlines()
        if len(lines) > 0:
          last_line = lines[-1]
          splits = last_line.split(";")
          if len(splits) > 0:
            self.build = int(splits[0]) + 1

  def update(self, library, method, datasets, method_param, base_param, result):
    with open(self.file, "a+") as f:
      runtime = 0
      if "runtime" in result:
        runtime = result["runtime"]

      f.write('%s;%s;%s;%s;%s;%s;%s;%s;\n' % (self.build, str(library),
        str(datasets), str(method), str(method_param), str(base_param),
        runtime, str(result)))
