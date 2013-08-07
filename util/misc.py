'''
  @file misc.py
  @author Marcus Edel

  Supporting functions.
'''

import os

'''
This function determinate if the given number is a float.

@param n - Number to test.
@return If the number a float returns True otherwise the function returns False.
'''
def isFloat(n):
  try:
    float(n)
  except ValueError as TypeError:
    return False
  else:
    return True

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
