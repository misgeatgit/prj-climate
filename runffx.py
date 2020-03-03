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

ffx_dir = 'data/ffx'
test_X = pds.read_csv('{}/natural_data_ffx_test_X.csv'.format(ffx_dir)).to_numpy()
test_Y = pds.read_csv('{}/natural_data_ffx_test_Y.csv'.format(ffx_dir)).to_numpy()
train_X = pds.read_csv('{}/natural_data_ffx_train_X.csv'.format(ffx_dir)).to_numpy()
train_Y = pds.read_csv('{}/natural_data_ffx_train_Y.csv'.format(ffx_dir)).to_numpy()

predictors = ['WMGHG', 'Ozone', 'Solar', 'Land_Use', 'SnowAlb_BC', 'Orbital',\
              'TropAerDir','TropAerInd','StratAer']

# Predict K years ahead
#Ks = [0,1,2,3,4,5,6,7,8,10,9]
Ks = [15,16,17,18,19,20]
for K in Ks:
    print('\nModels Predicting {} years ahead:'.format(K))
    cur_test_X = test_X[:len(test_X) - K]
    cur_test_Y = np.roll(test_Y, -K, axis=0)[:len(test_Y) - K]
    cur_train_X = train_X[:len(train_X) - K]
    cur_train_Y = np.roll(train_Y, -K, axis=0)[:len(train_Y) - K]
    #'''
    assert(cur_test_X.shape[0] == cur_test_Y.shape[0])
    assert(cur_train_X.shape[0] == cur_train_Y.shape[0])
    print('cur_test_X dim: {}'.format(cur_test_X.shape))
    models = ffx.run(cur_train_X, cur_train_Y, cur_test_X, \
                 cur_test_Y, predictors)
    best_performing_model={'sq_err':float('inf'), 'model':None}
    for model in models:
        yhat = model.simulate(cur_test_X)
        y = cur_test_Y
        print(' * {}'.format(model))
        sq_err = np.sum(np.square(y - yhat))
        print('   squared error= {}'.format(sq_err))
        if sq_err < best_performing_model['sq_err']:
            best_performing_model['sq_err'] = sq_err
            best_performing_model['model'] = model

    model = best_performing_model['model']
    yhat = model.simulate(cur_test_X)
    y = cur_test_Y
    plot_prediction_vs_actual(yhat, y,'predict_{}_years.png'.format(K),\
            '[Model: {}] [Squared Err={}]'.format(model, best_performing_model['sq_err']))
    '''
    FFX = ffx.FFXRegressor()
    FFX.fit(cur_train_X, cur_train_Y)
    #print("Prediction:", FFX.predict(cur_test_X))
    print(" Score(of best performing model):", FFX.score(cur_test_X, cur_test_Y))
    '''


