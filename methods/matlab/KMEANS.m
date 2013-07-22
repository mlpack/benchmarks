% @file KMEANS.m
% @author Marcus Edel
%
% K-Means Clustering with matlab.

function KMEANS(cmd)
% This program performs K-Means clustering on the given dataset.
%
% Required options:
%     (-i) [string]    Input dataset to perform clustering on.
%     (-I) [string]    Start with the specified initial centroids. 
%                      Default value ''.
% Options:
%     (-c) [int]    Number of clusters to find.
%     (-m) [int]    Maximum number of iterations before K-Means terminates. 
%                   Default value 1000.
%     (-s) [int]    Random seed.


% Load input dataset.
inputFile = regexp(cmd, '.*?-i ([^\s]+)', 'tokens', 'once');
X = csvread(inputFile{:});

% Check if centroid starting locations set is given.
C = [];
if strfind(cmd, '-I') > 0
    centroidFile = regexp(cmd, '.*?-I ([^\s]+)', 'tokens', 'once');
    C = csvread(centroidFile{:});
end

% Gather parameters.
clusters = str2double(regexp(cmd,'.* -c (\d+)','tokens','once'));
maxIterations = str2double(regexp(cmd,'.* -m (\d+)','tokens','once'));
seed = str2double(regexp(cmd,'.* -s (\d+)','tokens','once'));

% Validate parameters.
if isempty(maxIterations)
  m = 1000;
else
  if maxIterations == 0
    m = inf;
  elseif maxIterations
    m = maxIterations;
  end
end

if ~isempty(seed)
  s = RandStream('mt19937ar', 'Seed', seed);
  RandStream.setGlobalStream(s);
end

total_time = tic;
if ~isempty(clusters)
    [IDX, C] = kmeans(X, clusters, 'EmptyAction', 'singleton', ...
            'MaxIter', m);
    disp(sprintf('[INFO ]   total_time: %fs', toc(total_time)))
elseif ~isempty(C)
    [IDX, C] = kmeans(X, size(C, 1), 'Start', C, 'EmptyAction', ...
            'singleton', 'MaxIter', m);
    disp(sprintf('[INFO ]   total_time: %fs', toc(total_time)))
end

end
