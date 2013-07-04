% @file NBC.m
% @author Marcus Edel
%
% Naive Bayes Classifier with matlab.

function nbc(cmd)
%This program trains the Naive Bayes classifier on the given labeled 
% training set and then uses the trained classifier to classify the points
% in the given test set. Labels are expected to be the last row of the 
% training set.
%
% Required options:
%     (-T) [string]    A file containing the test set.
%     (-t) [string]    A file containing the training set.

trainFile = regexp(cmd, '.*?-t ([^\s]+)', 'tokens', 'once');
testFile = regexp(cmd, '.*?-T ([^\s]+)', 'tokens', 'once');

% Load input dataset.
TrainData = csvread(trainFile{:});
TestData = csvread(testFile{:});

% Use the last row of the training data as the labels.
labels = TrainData(:,end);
% Remove the label row.
TrainData = TrainData(:,1:end-1);

% Create and train the classifier.
total_time = tic;
classifier = NaiveBayes.fit(TrainData, labels);
% Run Naive Bayes Classifier on the test dataset.
labels = classifier.predict(TestData);

disp(sprintf('[INFO ]   total_time: %fs', toc(total_time)))
end
