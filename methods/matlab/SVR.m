% @file SVR.m
%
% Support Vector Regression with matlab.
% Requires Statistics and Machine Learning toolbox installed.
function svr(cmd)
% This program trains the Support Vector Regressor on the given labeled
% training set and then uses the trained classifier to classify the points
% in the given test set. Labels are expected to be the last row of the
% training set.
%
% Required options:
%     (-T) [string]    A file containing the test set.
%     (-t) [string]    A file containing the training set.
%     (-k) [string]    Name of the kernel.
%     (--max_iter) [int] Maximum iterations.

trainFile = regexp(cmd, '.*?-t ([^\s]+)', 'tokens', 'once');
testFile = regexp(cmd, '.*?-T ([^\s]+)', 'tokens', 'once');
kernel = regexp(cmd, '.*?-k ([^\s]+)', 'tokens', 'once');
maxIter = regexp(cmd, '.*?--max_iter ([^\s]+)', 'tokens', 'once'); 

% Load input dataset.
TrainData = csvread(trainFile{:});
TestData = csvread(testFile{:});

% Use the last row of the training data as the labels.
labels = TrainData(:,end);
% Remove the label row.
TrainData = TrainData(:,1:end-1);

% Create and train the classifier.
total_time = tic;
model = fitrsvm(TrainData, labels, 'KernelFunction', char(kernel),...
 'NumPrint', str2num(maxIter{1}));
predictions = predict(model, TestData);
disp(sprintf('[INFO ]   total_time: %fs', toc(total_time)));

% Save prediction of each class for test data.
csvwrite('predictions.csv', labels);

end

