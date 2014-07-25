% @file PERCEPTRON.m
% @author Anand Soni
%
% Perceptron with matlab.

function perceptron(cmd)
% Perceptron and Prediction.
%
% Required options:
%     (-t) [string]    File containing the train set.
%     (-T) [string]    File containing the test set.
%
% Options:
%     (-l) [string]    A file containing labels for the training set.
%     (-i) [int]       The maximum number of iterations the perceptron
%                      is to be run  Default value 1000.

%Load input dataset.
trainFile = regexp(cmd, '.*?-t ([^\s]+)', 'tokens', 'once');
testFile = regexp(cmd, '.*?-T ([^\s]+)', 'tokens', 'once');
labelsFile = regexp(cmd, '.*?-l ([^\s]+)', 'tokens', 'once');
iterations = str2double(regexp(cmd,'.* -i (\d+)','tokens','once'));

X = csvread(trainFile{:})';

if isempty(labelsFile)
  y = X(end,:);
  X = X(1:end-1,:);
else
  y = csvread(labelsFile{:})';
end

if isempty(iterations)
  iterations = 1000;
end

% Perform perceptron prediction.
total_time = tic;

net = perceptron;
net.trainParam.epochs = iterations;
net = train(net,X,y);

if ~isempty(testFile)
    % Predicted the classes.
    testSet = csvread(testFile{:})';
    predictions = net(testSet)';
end

disp(sprintf('[INFO ]   total_time: %fs', toc(total_time)))

if ~isempty(testFile)
    csvwrite('matlab_pc_predictions.csv', predictions);
end

end
