% @file LOGISTIC_REGRESSION.m
% @author Marcus Edel
%
% Logistic Regression with matlab.

function logistic_regression(cmd)
% Logistic Regression and Prediction.
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
  y = X(:,end) + 1; % We have to increment because labels must be positive.
  X = X(:,1:end-1);
else
  y = csvread(responsesFile{:});
end

% Perform logistic regression.
total_time = tic;
B = mnrfit(X, y);

if ~isempty(testFile)
    % Predicted the classes.
    testSet = csvread(testFile{:});
    predictions = mnrval(B, testSet);
    % Map the probabilities to the actual classes.
    [~, idx] = max(predictions, [], 2);
end

disp(sprintf('[INFO ]   total_time: %fs', toc(total_time)))

if ~isempty(testFile)
    csvwrite('predictions.csv', idx - 1); % Subtract extra label bit.
    csvwrite('matlab_lr_probs.csv', predictions);
end

if ~isempty(estimatesFile)
    csvwrite(estimatesFile{:});
end

end
