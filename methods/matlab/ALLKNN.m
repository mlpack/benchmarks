% @file ALLKNN.m
% @author Marcus Edel
%
% All K-Nearest-Neighbors with matlab.

function allknn(cmd)
% This program will calculate the all k-nearest-neighbors of a set of 
% points using kd-trees. You may specify a separate set of reference points
% and query points, or just a reference set which will be used as both the 
% reference and query set.
%
% Required options:
%     (-k) [int]       Number of furthest neighbors to find.
%     (-t) [string]    A file containing the training set.
%
% Options:
%     (-l) [int]       Leaf size for tree building. Default value 20.
%     (-N)             If true, O(n^2) naive mode is used for computation.
%     (-q) [string]    File containing query points (optional). 
%                      Default value ''.

% Load input dataset.
referenceFile = regexp(cmd, '.*?-r ([^\s]+)', 'tokens', 'once');
referenceData = csvread(referenceFile{:});

% Get all the parameters.
queryFile = regexp(cmd, '.*?-q ([^\s]+)', 'tokens', 'once');
k = regexp(cmd,'.* -k (\d+)','tokens','once');
leafSize = str2double(regexp(cmd,'.* -l (\d+)','tokens','once'));

if ~isempty(queryFile)
  disp('[INFO ] Load query data.');
  queryData = csvread(queryFile{:});
end

if ~isempty(k)
  k = str2double(k)
else
  disp('[Fatal] Required options: Number of furthest neighbors to find.');
  return;
end

total_time = tic;
% Sanity check on k value: must be greater than 0, must be less than the
% number of reference points.
if k > size(referenceData, 2)
  msg = [...
      '[Fatal] Invalid k: %i; must be greater than 0 and less '...
      'than or equal to the number of reference points (%i)'...
      ];
  disp(sprintf(msg, k, size(referenceData, 2)))
  return;
end

if isempty(leafSize)
  leafSize = 20;  
end

if strfind(cmd, '-N') > 0
  if isempty(queryFile)
    [IDX, D] = knnsearch(referenceData, referenceData, 'K', k, ...
      'distance', 'euclidean', 'NSMethod', 'exhaustive');    
  else
    [IDX, D] = knnsearch(referenceData, queryData, 'K', k, ...
      'distance', 'euclidean', 'NSMethod', 'exhaustive');
  end
else
  if isempty(queryFile)
    [IDX, D] = knnsearch(referenceData, referenceData, 'K', k, ...
      'distance', 'euclidean', 'NSMethod', 'kdtree', 'BucketSize', ...
      leafSize);
  else
    [IDX, D] = knnsearch(referenceData, queryData, 'K', k, ...
        'distance', 'euclidean', 'NSMethod', 'kdtree', 'BucketSize', ...
        leafSize); 
    end
end

disp(sprintf('[INFO ]   total_time: %fs', toc(total_time)))
end
