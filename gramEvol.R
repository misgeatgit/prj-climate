library("gramEvol")
library("Metrics")
library("sets")

df = read.csv("/home/misgana/Desktop/prj-climate/data/ffx/natural_data_ffx.csv")
Input <- subset(df, select=-c(Year,Temperature))
Output <- subset(df, select=c(Temperature))
print(nrow((Input)))
print(nrow(Output))
shift <- function(d, k) rbind( tail(d,k), head(d,-k), deparse.level = 0 )
LookAhead <- 1:1
for( LA in LookAhead) {
    X <- head(Input, nrow(Input)-LA)
    print(sprintf("NumOfRows(X): %d",nrow(X)))
    WMGHG <- X[, "WMGHG"]
    Ozone <- X[,"Ozone"]
    Solar <- X[,"Solar"]
    Land_Use <- X[,"Land_Use"]
    SnowAlb_BC <- X[,"SnowAlb_BC"]
    Orbital <- X[,"Orbital"]
    TropAerDir <- X[, "TropAerDir"]
    TropAerInd <- X[, "TropAerInd"]
    StratAer <- X[, "StratAer"]
    #Ocean <- X[, "Ocean"]
    
    #y <- head(shift(Output, -LA), nrow(Output)-LA)
    Temperature <- tail(Output, -LA)[, "Temperature"]
    print(sprintf("LengthOf(Temperature): %d",length(Temperature)))
    # TODO explore better cost function which suits this particular prediction problem.
    SymRegFitFunc <- function(expr) {
        result <- eval(expr)
        if (any(is.nan(result)))
            return(Inf)
        #return (mean(log(1 + abs(Temperature - result)))) # ActualOutput Vs Predicted
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
    ruleDefs <- list(pair(ruleDef=group0_ruleDef,name="group_0"))

    for(P in ruleDefs) {   
        grammarDef <- CreateGrammar(P$ruleDef)
        set.seed(2)
        suppressWarnings(ge <- GrammaticalEvolution(grammarDef, SymRegFitFunc, terminationCost = 0.005))
        # TODO save output to a dataFrame
        print(ge)
        png(file=sprintf("%s_LA_%s.png",P$name, LA))
        plot(Temperature, col= "green", type="p")
        points(eval(ge$best$expressions), col = "blue", type = "p")
        dev.off()
    }
}
# How to evaluate? Test set?
#ruleDef <- list(expr = grule(op(expr, expr), func(expr), var),
#                func = grule(sin, cos, tan, log, sqrt),
#                op = grule('+', '-', '*', '/', '^'),
#                var = grule(distance, n), # Input feature vectors here
#                n = grule(1, 2, 3, 4, 5, 6, 7, 8, 9))