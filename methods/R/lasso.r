
# Read the command line arguments in a vector.
library(mlr)
library(tictoc)
myArgs <- commandArgs(trailingOnly = TRUE)

trainFile <- myArgs[2]
lambda1 <- as.numeric(myArgs[4])

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

lasso.learner <- makeLearner("regr.penalized.lasso", par.vals = list(lambda1 = lambda1))
fmodel <- train(lasso.learner, trainTask)
fpmodel <- predict(fmodel, trainTask)
toc(log = TRUE)

out <- capture.output(tic.log(format = TRUE))
cat(out, file="log.txt", append=FALSE)

pred <- as.numeric(fpmodel$data$response)
write.csv(pred, "predictions.csv", row.names = F)
