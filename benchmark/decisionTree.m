function decisionTree(TRAINx,TRAINy,TESTx, TESTy)
%the input values are csv files containing features (TRAINx and TESTx) and labels (TRAINy and TESTy)

%reading the csv file 
X=csvread(TRAINx);
Y=csvread(TRAINy);
testX=csvread(TESTx);
testY=csvread(TESTy);

total_time = tic;
%This will return a fitted binary classification decision treebased on the input variables contained in matrix X and output Y.
%The returned binary tree splits branching nodes based on the values of a column of X.
B=fitctree(X,Y,'MinLeafSize',10);
predictY = predict(B, testX);
accuracy = (sum(predictY == testY) / numel(testY))*100;
disp(sprintf('accuracy of prediction (%): %f',accuracy));

%This will return the time taken to run this function
disp(sprintf('total_time taken: %fs', toc(total_time)));
end
