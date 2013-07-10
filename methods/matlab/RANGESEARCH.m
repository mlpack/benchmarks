% @file RANGESEARCH.m
% @author Marcus Edel
%
% Range Search with matlab.

function rangesearch(cmd)
% This program implements range search with a Euclidean distance metric. 
% For a given query point, a given range, and a given set of reference 
% points, the program will return all of the reference points with distance
% to the query point in the given range.  
%
% Required options:
%     (-M) [double]    Upper bound in range.
%     (-r) [string]    File containing the reference dataset.
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
max = regexp(cmd,'.* -M ([0-9]*\.?[0-9])','tokens','once');
queryFile = regexp(cmd, '.*?-q ([^\s]+)', 'tokens', 'once');
leafSize = str2double(regexp(cmd,'.* -l (\d+)','tokens','once'));

if ~isempty(max)
  max = str2double(max);
else
  disp('[Fatal] Required options: Upper bound in range.');
  return;
end

if ~isempty(queryFile)
  disp('[INFO ] Load query data.');
  queryData = csvread(queryFile{:});
end

total_time = tic;

if isempty(leafSize)
  leafSize = 20;  
end

% Perform range search.
if strfind(cmd, '-N') > 0
  if isempty(queryFile)
    [idx, dist] = rangesearch(referenceData, referenceData, max,...
      'Distance', 'euclidean', 'NSMethod', 'exhaustive');
  else
    [idx, dist] = rangesearch(referenceData, queryData, max, 'Distance',...
      'euclidean', 'NSMethod', 'exhaustive');
  end
else
  if isempty(queryFile)
    [idx, dist] = rangesearch(referenceData, referenceData, max,...
      'Distance', 'euclidean', 'NSMethod', 'kdtree', 'BucketSize', leafSize);    
  else
    [idx, dist] = rangesearch(referenceData, queryData, max, 'Distance',...
      'euclidean', 'NSMethod', 'kdtree', 'BucketSize', leafSize);
  end  
end

disp(sprintf('[INFO ]   total_time: %fs', toc(total_time)))
end
