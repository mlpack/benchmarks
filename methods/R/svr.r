# Read the command line arguments in a vector.
library(mlr)
library(tictoc)
myArgs <- commandArgs(trailingOnly = TRUE)

trainFile <- myArgs[2]
kernel <- myArgs[4]
c <- as.numeric(myArgs[6])
epsilon <- as.numeric(myArgs[8])
gamma <- as.numeric(myArgs[10])

trainData <- read.csv(trainFile, header = FALSE, sep = ",")

names = character()
for ( i in 1:ncol(trainData) )
{
  names[length(names) + 1] = paste("V", toString(i), sep = "")
}
names(trainData) = names
tar = paste("V", toString(ncol(trainData)), sep = "")
tic()
trainTask <- makeRegrTask(data = trainData, target = tar)

lr.learner <- makeLearner("regr.svm", par.vals = list(kernel = kernel, cost = c, epsilon = epsilon, gamma = gamma))
fmodel <- train(lr.learner, trainTask)
fpmodel <- predict(fmodel, trainTask)
toc(log = TRUE)

out <- capture.output(tic.log(format = TRUE))
cat(out, file="log.txt", append=FALSE)

pred <- as.numeric(fpmodel$data$response)


