install.packages('mlr', repos='http://cran.us.r-project.org')
install.packages('tictoc', repos='http://cran.us.r-project.org')

# Read the command line arguments in a vector.
library(mlr)
library(tictoc)
myArgs <- commandArgs(trailingOnly = TRUE)

trainFile <- myArgs[2]
testFile <- myArgs[4]

trainData <- read.csv(trainFile, header = FALSE, sep = ",")
testData <- read.csv(testFile, header = FALSE, sep = ",")

names = character()
for ( i in 1:ncol(trainData) )
{
  names[length(names) + 1] = paste("V", toString(i), sep = "")
}
names(trainData) = names
testData[, ncol(trainData)] = sample(0:1, size = nrow(testData), replace = T)
names(testData) = names

tar = paste("V", toString(ncol(trainData)), sep = "")

tic()
trainTask <- makeClassifTask(data = trainData, target = tar)
testTask <- makeClassifTask(data = testData, target = tar)

qda.learner <- makeLearner("classif.qda", predict.type = "response")
fmodel <- train(qda.learner,trainTask)
fpmodel <- predict(fmodel, testTask)
toc(log = TRUE)

out <- capture.output(tic.log(format = TRUE))
cat(out, file="log.txt", append=FALSE)

pred <- as.numeric(fpmodel$data$response)
write.csv(pred, "predictions.csv", row.names = F)
