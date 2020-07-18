library("gramEvol")
library("Metrics")
library("sets")

MAX_ITER <- 10000
MAX_LA <- 30

df = read.csv("/home/misgana/Desktop/prj-climate/data/ffx/natural_data_ffx.csv")
Input <- subset(df, select=-c(Year,Temperature))
Output <- subset(df, select=c(Temperature))
shift <- function(d, k) rbind( tail(d,k), head(d,-k), deparse.level = 0 )
LookAhead <- 1:MAX_LA
metrics0 <- data.frame(LookAheadYears=c(1:MAX_LA), model=c(1:MAX_LA), MAE_on_train=c(1:MAX_LA), MAE_on_test=c(1:MAX_LA),stringsAsFactors = FALSE)
metrics1 <- data.frame(LookAheadYears=c(1:MAX_LA), model=c(1:MAX_LA), MAE_on_train=c(1:MAX_LA), MAE_on_test=c(1:MAX_LA),stringsAsFactors = FALSE)
metrics2 <- data.frame(LookAheadYears=c(1:MAX_LA), model=c(1:MAX_LA), MAE_on_train=c(1:MAX_LA), MAE_on_test=c(1:MAX_LA),stringsAsFactors = FALSE)
metrics3 <- data.frame(LookAheadYears=c(1:MAX_LA), model=c(1:MAX_LA), MAE_on_train=c(1:MAX_LA), MAE_on_test=c(1:MAX_LA),stringsAsFactors = FALSE)
for( LA in LookAhead) {
    X <- head(Input, nrow(Input)-LA)
    TrainLen <- as.integer(nrow(X)*.8)
    TestLen <- nrow(X) - TrainLen
    XTrain <- head(X, TrainLen)
    XTest  <- tail(X, TestLen)
    print(sprintf("NumOfRows(X): %d",nrow(X)))
    WMGHG <- XTrain[, "WMGHG"]
    Ozone <- XTrain[,"Ozone"]
    Solar <- XTrain[,"Solar"]
    Land_Use <- XTrain[,"Land_Use"]
    SnowAlb_BC <- XTrain[,"SnowAlb_BC"]
    Orbital <- XTrain[,"Orbital"]
    TropAerDir <- XTrain[, "TropAerDir"]
    TropAerInd <- XTrain[, "TropAerInd"]
    StratAer <- XTrain[, "StratAer"]
    #Ocean <- XTrain[, "Ocean"]

    Y <- tail(Output, -LA) 
    YTrain <- head(Y, TrainLen)
    YTest <- head(Y, TestLen)
    Temperature <- YTrain[, "Temperature"]
    print(sprintf("LengthOf(Temperature): %d",length(Temperature)))
    SymRegFitFunc <- function(expr) {
        result <- eval(expr)
        if (any(is.nan(result)))
            return(Inf)
        return (mae(Temperature, result))
    }
    # TODO Try various possible grammars
    group0_ruleDef <- list(expr = grule(op(expr, expr), func(expr), var1, var2, var3),
                    func = grule(sin, cos, tan, log, sqrt, exp),
                    op = grule('+', '-', '*', '/', '^'),
                    var1 = grule(WMGHG),
                    var2 = grule(Ozone),
                    var3 = grule(TropAerDir))
    group1_ruleDef <- list(expr = grule(op(expr, expr), func(expr), var1, var2, var3, var4),
                            func = grule(sin, cos, tan, log, sqrt),
                            op = grule('+', '-', '*', '/', '^'),
                            var1 = grule(WMGHG),
                            var2 = grule(Ozone),
                            var3 = grule(Land_Use),
                            var4 = grule(TropAerDir))
    group2_ruleDef <- list(expr = grule(op(expr, expr), func(expr), var1, var2, var3, var4),
                            func = grule(sin, cos, tan, log, sqrt),
                            op = grule('+', '-', '*', '/', '^'),
                            var1 = grule(WMGHG),
                            var2 = grule(Ozone),
                            var3 = grule(TropAerInd),
                            var4 = grule(TropAerDir))
    allVar_ruleDef <- list(expr = grule(op(expr, expr), func(expr), var1, var2, var3, var4, var5, var6, var7, var8, var9),
                            func = grule(sin, cos, tan, log, sqrt),
                            op = grule('+', '-', '*', '/', '^'),
                            var1 = grule(WMGHG),
                            var2 = grule(Ozone),
                            var3 = grule(Solar),
                            var4 = grule(Land_Use),
                            var5 = grule(SnowAlb_BC),
                            var6 = grule(Orbital),
                            var7 = grule(TropAerDir),
                            var8 = grule(TropAerInd),
                            var9 = grule(StratAer))
    ruleDefs <- list(pair(ruleDef=group0_ruleDef,name="group_0"), pair(ruleDef=group1_ruleDef,name="group_1"),
                     pair(ruleDef=group2_ruleDef, name="group_2"), pair(ruleDef=allVar_ruleDef,name="group_all"))
    #ruleDefs <- list(pair(ruleDef=group0_ruleDef,name="all_var"))

    for(P in ruleDefs) {   
        grammarDef <- CreateGrammar(P$ruleDef)
        set.seed(2)
        suppressWarnings(ge <- GrammaticalEvolution(grammarDef, SymRegFitFunc, iterations=MAX_ITER, terminationCost = 0.005, monitorFunc=print))
        png(file=sprintf("%s_LA_%s.png",P$name, LA))
        plot(Temperature, col= "green", type="p", xlab="day", ylab="Temperature")
        predicted <- eval(ge$best$expressions)
        points(predicted, col = "blue", type = "l")
        legend(x="topleft",y=2, legend=c("Actual", sprintf("%s",ge$best$expressions)),col=c("green", "blue"), pch=c(".","-"))
        dev.off()
        metrics <- c(sprintf("%s", ge$best$expressions), mae(YTrain[, "Temperature"], predicted), 
                      mae(YTest[, "Temperature"], eval(ge$best$expressions, XTest)))
        if(P$name == "group_0") {
           metrics0$model[LA] = metrics[1]
           metrics0$MAE_on_train[LA] = metrics[2]
           metrics0$MAE_on_test[LA] = metrics[3]
        } else if (P$name == "group_1") { 
           metrics1$model[LA] = metrics[1]
           metrics1$MAE_on_train[LA] = metrics[2]
           metrics1$MAE_on_test[LA] = metrics[3]
        } else if (P$name == "group_2") {
           metrics2$model[LA] = metrics[1]
           metrics2$MAE_on_train[LA] = metrics[2]
           metrics2$MAE_on_test[LA] = metrics[3]
        } else {
           metrics3$model[LA] = metrics[1]
           metrics3$MAE_on_train[LA] = metrics[2]
           metrics3$MAE_on_test[LA] = metrics[3]
        } 
    }
}

# Save Metrics
write.csv(metrics0,"Group_0_Metrics.csv", row.names = FALSE)
write.csv(metrics1,"Group_1_Metrics.csv", row.names = FALSE)
write.csv(metrics2,"Group_2_Metrics.csv", row.names = FALSE)
write.csv(metrics3,"Group_3_Metrics.csv", row.names = FALSE)