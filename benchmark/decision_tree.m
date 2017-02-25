function decision_tree(cmd)

% Decision Tree and prediction
%
% Required options:
%     (-i) [string]    File containing X (predictors).
%
% Options:
%     (-r) [string]    File containing y (responses). If not given, the
%                      responses are assumed to be the last row of the
%                      input file.
%     (-t) [string]    File containing test dataset.
%     (-o) [string]    This file is where the predicted responses will be
%                      saved

% Load input dataset.
regressorsFile = regexp(cmd, '.*?-i ([^\s]+)', 'tokens', 'once');
responsesFile = regexp(cmd, '.*?-r ([^\s]+)', 'tokens', 'once');
testFile = regexp(cmd, '.*?-t ([^\s]+)', 'tokens', 'once');
estimatesFile = regexp(cmd, '.*?-o ([^\s]+)', 'tokens', 'once');

X = csvread(regressorsFile{:});

if isempty(responsesFile)
  y = X(:,end);
  X = X(:,1:end-1);
else
  y = csvread(responsesFile{:});
end

total_time = tic;


%This will return a fitted binary classification decision treebased on the input variables contained in matrix X and output Y.
%The returned binary tree splits branching nodes based on the values of a column of X.
B=fitctree(X,y);

if ~isempty(testFile)
    % Predict the classes.
    testSet = csvread(testFile{:});
    predictions = predict(B, testSet);
    % Map the probabilities to the actual classes.
    [~, idx] = max(predictions, [], 2);
end


%This will return the time taken to run this function
disp(sprintf('[INFO ]   total_time: %fs', toc(total_time)))


if ~isempty(testFile)
    csvwrite('predictions.csv', idx);
    csvwrite('matlab_decision_tree_probs.csv', predictions);
end

if ~isempty(estimatesFile)
    csvwrite(estimatesFile{:});
end

end
