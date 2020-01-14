import pandas as pds
import numpy as np
import ffx

test_X = pds.read_csv('natural_data_ffx_test_X.csv').values
test_Y = pds.read_csv('natural_data_ffx_test_Y.csv').values
train_X = pds.read_csv('natural_data_ffx_train_X.csv').values
train_Y = pds.read_csv('natural_data_ffx_train_Y.csv').values

predictors = ['WMGHG', 'Ozone', 'Solar', 'Land_Use', 'SnowAlb_BC', 'Orbital',\
              'TropAerDir','TropAerInd','StratAer']

# Predict K years ahead
Ks = [0,1,2,3,4,5]
for K in Ks:
    print('\nModels Predicting {} years ahead:'.format(K))
    test_X = test_X[:len(test_X) - K]
    test_Y = np.roll(test_Y, -K, axis=0)[:len(test_Y) - K]
    train_X = train_X[:len(train_X) - K]
    train_Y = np.roll(train_Y, -K, axis=0)[:len(train_Y) - K]
    #'''
    models = ffx.run(train_X, train_Y, test_X, \
                 test_Y, predictors)
    for model in models:
        yhat = model.simulate(test_X)
        y = test_Y
        print(' * {}'.format(model))
        print('   squared error= {}'.format(np.sum(np.square(y - yhat))))
    '''
    FFX = ffx.FFXRegressor()
    FFX.fit(train_X, train_Y)
    #print("Prediction:", FFX.predict(test_X))
    print(" Score(of best performing model):", FFX.score(test_X, test_Y))
    '''
