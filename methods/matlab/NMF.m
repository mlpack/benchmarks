% @file NMF.m
% @author Marcus Edel
%
% Non-negative Matrix Factorization with matlab.

function nmf(cmd)
% This program performs non-negative matrix factorization on the given 
% dataset, storing the resulting decomposed matrices in the specified 
% files. For an input dataset V, NMF decomposes V into two matrices W and H
% such that
%  
%  V = W * H
%  
%  where all elements in W and H are non-negative.
%
% Required options:
%     (-i) [string]    Input dataset to perform NMF on.
%     (-r) [int]       Rank of the factorization.
% Options:
%  (-m) [int]          Number of iterations before NMF terminates (0) runs 
%                      until convergence. Default value 10000.
%  (-e) [double]       The minimum root mean square residue allowed for 
%                      each iteration, below which the program terminates.
%                      Default value 1e-05.
%  (-s) [int]          Random seed.
%  (-u) [string]       Update rules for each iteration; ( multdist | als ).
%                      Default value 'multdist'.


% Load input dataset.
inputFile = regexp(cmd, '.*?-i ([^\s]+)', 'tokens', 'once');
X = csvread(inputFile{:});

total_time = tic;

% Gather parameters.
rank = str2double(regexp(cmd,'.* -r (\d+)','tokens','once'));
seed = str2double(regexp(cmd,'.* -s (\d+)','tokens','once'));
maxIterations = str2double(regexp(cmd,'.* -m (\d+)','tokens','once'));
minResidue = str2double(regexp(cmd, '.*?-e ([^\s]+)', 'tokens', 'once'));
updateRule = regexp(cmd, '.*?-u ([^\s]+)', 'tokens', 'once');

% Validate parameters.
if isempty(maxIterations)
  m = 10000;
else
  if maxIterations == 0
    m = inf;
  else
    m = maxIterations;
  end
end

if isempty(minResidue)
  e = 1e-05;
else
  e = minResidue; 
end

if ~isempty(seed)
  s = RandStream('mt19937ar','Seed', seed);
  RandStream.setGlobalStream(s);
end

if isempty(rank) || rank < 1
   disp('[Fatal] The rank of the factorization cannot be less than 1.')
   return
end

if ~strcmp(updateRule, 'multdist') && ~strcmp(updateRule, 'als')
  msg = [...
      '[Fatal] Invalid update rules ("%s") must be "multdist" or "als"'];
  disp(sprintf(msg, updateRule{:}))
  return
end

% Perform NMF with the specified update rules and parameters.
opt = statset('MaxIter', m, 'TolFun', e, 'TolX', e);
if strcmp(updateRule, 'multdist') || ~strcmp(updateRule, 'als')
  nnmf(X, rank, 'options', opt, 'algorithm', 'mult');
  disp(sprintf('[INFO ]   total_time: %fs', toc(total_time)))
elseif strcmp(updateRule, 'als')
  nnmf(X, rank, 'options', opt, 'algorithm', 'als');
  disp(sprintf('[INFO ]   total_time: %fs', toc(total_time)))
end

end
