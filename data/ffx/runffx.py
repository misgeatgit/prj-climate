import pandas as pds
import matplotlib.pyplot as plt
import numpy as np
import ffx
from textwrap import wrap

def plot_prediction_vs_actual(yhat, y, file_name, title=''):
        fig = plt.figure()
        ax = plt.subplot(111)
        ax.plot(yhat, 'ro', label='Predicted')
        ax.plot(y, 'bo', label='Actual')
        ax.legend()
        plt.rcParams['axes.titlepad'] = 20
        plt.rcParams["axes.titlesize"] = 8
        #plt.title("\n".join(wrap(title,80)))
        #plt.text(0.5, 0.5, "\n".join(wrap(title,80)), fontsize=9)
        fig.savefig(file_name, dpi=fig.dpi)
        plt.close()

test_X = pds.read_csv('natural_data_ffx_test_X.csv').values
test_Y = pds.read_csv('natural_data_ffx_test_Y.csv').values
train_X = pds.read_csv('natural_data_ffx_train_X.csv').values
train_Y = pds.read_csv('natural_data_ffx_train_Y.csv').values

predictors = ['WMGHG', 'Ozone', 'Solar', 'Land_Use', 'SnowAlb_BC', 'Orbital',\
              'TropAerDir','TropAerInd','StratAer']

# Predict K years ahead
Ks = [10]
for K in Ks:
    print('\nModels Predicting {} years ahead:'.format(K))
    test_X = test_X[:len(test_X) - K]
    test_Y = np.roll(test_Y, -K, axis=0)[:len(test_Y) - K]
    train_X = train_X[:len(train_X) - K]
    train_Y = np.roll(train_Y, -K, axis=0)[:len(train_Y) - K]
    #'''
    models = ffx.run(train_X, train_Y, test_X, \
                 test_Y, predictors)
    best_performing_model={'sq_err':float('inf'), 'model':None}
    for model in models:
        yhat = model.simulate(test_X)
        y = test_Y
        print(' * {}'.format(model))
        sq_err = np.sum(np.square(y - yhat))
        print('   squared error= {}'.format(sq_err))
        if sq_err < best_performing_model['sq_err']:
            best_performing_model['sq_err'] = sq_err
            best_performing_model['model'] = model

    model = best_performing_model['model']
    yhat = model.simulate(test_X)
    y = test_Y
    plot_prediction_vs_actual(yhat, y,'predict_{}_years.png'.format(K),\
            '[Model: {}] [Squared Err={}]'.format(model, best_performing_model['sq_err']))
    '''
    FFX = ffx.FFXRegressor()
    FFX.fit(train_X, train_Y)
    #print("Prediction:", FFX.predict(test_X))
    print(" Score(of best performing model):", FFX.score(test_X, test_Y))
    '''


