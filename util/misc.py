'''
  @file misc.py
  @author Marcus Edel

  Supporting functions.
'''

import os

'''
This function determinate if the given number is a float.

@param n - Number to test.
@return If the number is a float return True otherwise return False.
'''
def isFloat(n):
  try:
    float(n)
  except ValueError as TypeError:
    return False
  else:
    return True

'''
Function to seach the minimum scalar in a list.

@param data - A list that contains the values.
@return The minimum scalar of the given list.
'''
def minData(data):
  minData = float('Inf')
  for d in data:
    if isFloat(d) and d < minData:
      minData = d
  return minData

'''
Count all datasets to determine the dataset size.

@param libraries - Contains the Dataset List.
@return Dataset count.
'''
def CountLibrariesDatasets(libraries):
  datasetList = []
  for libary, data in libraries.items():
    for dataset in data:
      if not dataset[0] in datasetList:
        datasetList.append(dataset[0])

  return len(datasetList)

'''
Add all rows from a given matrix to a given table.

@param matrix - 2D array contains the row.
@param table - Table in which the rows are inserted.
@return Table with the inserted rows.
'''
def AddMatrixToTable(matrix, table):
  for row in matrix:
    table.append(row)
  return table

'''
Normalize the dataset name. If the dataset is a list of datasets, take the first
dataset as name. If necessary remove characters like '.', '_'.

@param dataset - Dataset file or a list of datasets files.
@return Normalized dataset name.
'''
def NormalizeDatasetName(dataset):
  if not isinstance(dataset, str):
    return os.path.splitext(os.path.basename(dataset[0]))[0].split('_')[0]
  else:
    return os.path.splitext(os.path.basename(dataset))[0].split('_')[0]

'''
Search the correct row to insert the new data. We look at the left column for
a free place or for the matching name.

@param dataMatrix - In this Matrix we search for the right position.
@param datasetName - Name of the dataset.
@param datasetCount - Maximum dataset count.
'''
def FindRightRow(dataMatrix, datasetName, datasetCount):
  for row in range(datasetCount):
    if (dataMatrix[row][0] == datasetName) or (dataMatrix[row][0] == "-"):
      return row

'''
Collect informations for the given dataset.

@param path - Path to the dataset.
@return Tuble which contains the informations about the given dataset.
'''
def DatasetInfo(path):
  if not isinstance(path, str):
    path = path[0]

  instances = 0
  with open(path, "r") as fid:
    for line in fid:
      instances += 1

  attributes = 0
  with open(path, "r") as fid:
    for line in fid:
      attributes = line.count(",") + 1
      break

  name = NormalizeDatasetName(path)
  size = os.path.getsize(path) / (1 << 20)
  datasetType = "real"

  return (name, size, attributes, instances, datasetType)

'''
This function Remove a given file or list of files.

@param dataset - File or list of file which should be deleted.
'''
def RemoveDataset(dataset):
  if isinstance(dataset, str):
    dataset = [dataset]

  for f in dataset:
    if os.path.isfile(f):
      os.remove(f)

'''
Check if the given file is available.

@param fileName - The name of the file.
@return True if the file is available otherwise False.
'''
def CheckFileAvailable(fileName):
    return True if os.path.isfile(fileName) else False

'''
Check if the file is available in one of the given formats.

@param dataset - Datsets which should be checked.
@param formats - List of supported file formats.
@return Orginal dataset or dataset with the new file format.
'''
def CheckFileExtension(dataset, formats):
  dataExtension = os.path.splitext(dataset)[1][1:]
  if dataExtension in formats:
    return dataset
  else:
    return dataset[0:len(dataset) - len(dataExtension)] + formats[0]

'''
Create the directory structure for the scripts.

@param directories - List of directories to create.
'''
def CreateDirectoryStructure(directories):
  for directory in directories:
    if not os.path.exists(directory):
       os.makedirs(directory)
