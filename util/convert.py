'''
  @file convert.py
  @author Marcus Edel

  Implementation of the Convert class.
'''

import os, sys, inspect

# Import the util path, this method even works if the path contains
# symlinks to modules.
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(
  os.path.split(inspect.getfile(inspect.currentframe()))[0], "")))
if cmd_subfolder not in sys.path:
  sys.path.insert(0, cmd_subfolder)

from log import *

import os.path

'''
This class implements functions to convert files.
'''
class Convert(object):

  '''
  Convert the dataset to a file with the given extension.

  @param dataset - Convert the specified dataset.
  @param extension - Convert the dataset to a new file with the specified 
  extension.
  '''
  def __init__(self, dataset, extension):
    self.extension = extension
    self.modifiedDataset = ""

    self.ModifyDataset(dataset, extension)

  '''
  Decide which method we have to call to modify the dataset.

  @param dataset - Convert the specified dataset.
  @param extension - Convert the dataset to a new file with the specified 
  extension.
  '''
  def ModifyDataset(self, dataset, extension):
    dataExtension = os.path.splitext(dataset)[1][1:]
    newDataset = dataset[0:len(dataset) - len(dataExtension)] + extension

    # Currently the following conversions are implemented:
    # csv -> arff
    # txt -> arff 
    if extension == "arff" and (dataExtension == "csv" or dataExtension == "txt"):
      self.AddArffHeader(dataset, newDataset)
    else:
      Log.Fatal("No conversion possible.")
      pass

  '''
  Add the arff header to the dataset file.

  @param data - This dataset contains the information.
  @param newData - This dataset contains the information and the header.
  '''
  def AddArffHeader(self, data, newData):
    # Extract the dataset name.
    relationName = os.path.splitext(os.path.basename(data))[0].split('_')[0]

    # Read the first line to count the attributes.
    fid = open(data)
    head = [next(fid) for x in range(1)]
    fid.close()
    
    # We can convert files with ' ' and ',' as seperator.
    count = max(head[0].count(","), head[0].count(" ")) + 1

    # Write the arff header to the new file.
    nfid = open(newData, "a")
    nfid.write("@relation " + relationName + "\n\n")
    for i in range(count):
      nfid.write("@attribute " + data + "_dim" + str(i) + " NUMERIC\n")
    nfid.write("\n@data\n")

    # Append the data for the given file to the new arff file.
    fid = open(data, "r")
    while True:
      line = fid.read(65536)
      if line:
        nfid.write(line)
      else:
        break

    fid.close()
    nfid.close()

    # Add the modified datasetname to the list.
    self.modifiedDataset = newData
