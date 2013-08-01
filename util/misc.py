'''
  @file misc.py
  @author Marcus Edel

  Supporting functions.
'''

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
