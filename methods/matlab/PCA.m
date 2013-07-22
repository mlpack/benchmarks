% @file PCA.m
% @author Marcus Edel
%
% Principal Components Analysis with matlab.

function pca(cmd)
% This program performs principal components analysis on the given dataset.
% It will transform the data onto its principal components, optionally 
% performing dimensionality reduction by ignoring the principal components 
% with the smallest eigenvalues.
%
% Required options:
%     (-i) [string]    Input dataset to perform PCA on.
% Options:
%     (-d) [int]       Desired dimensionality of output dataset. If this 
%                      option not set no dimensionality reduction is 
%                      performed. Default value 0.
%     (-s)             If set, the data will be scaled before running PCA,
%                      such that the variance of each feature is 1.


inputFile = regexp(cmd, '.*?-i ([^\s]+)', 'tokens', 'once');

% Load input dataset.
X = csvread(inputFile{:});

% Find out what dimension we want.
k = str2double(regexp(cmd,'.* -d.* (\d+)','tokens','once'));
% Validate the parameter.
if k > 0
    if k > size(X, 2)
        msg = [...
            '[Fatal] New dimensionality (%i) cannot be greater than'...
            'existing dimensionality (%i)!'...
            ];
        disp(sprintf(msg, k, size(X, 2)))
        return
    end
end

total_time = tic;
% Retrieve the dimensions of X.
[m, n] = size(X);

% Get the options for running PCA.
if strfind(cmd, '-s') > 0
    % The princomp function centers X by subtracting off column means, but 
    % the function doesn't rescale the columns of X. So we have to rescale
    % before princomp. If X is m-by-n with m > n, then compute only the 
    % first n columns.
    if (m <= n)
        [~, score] = princomp(zscore(X));
    else
        [~, score] = princomp(zscore(X), 'econ');
    end        
else
    % Performs principal components analysis on the dataset X. If X is 
    % m-by-n with m > n, then compute only the first n columns.
    if (m <= n)
        [~, score] = princomp(X);
    else
        [~, score] = princomp(X, 'econ');
    end        
end

% Reduced data dimension.
if k > 0
   score = score(:,1:k);
end

disp(sprintf('[INFO ]   total_time: %fs', toc(total_time)))

end