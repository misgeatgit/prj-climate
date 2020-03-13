import pandas as pds
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import ffx
#import xgp # another symbolica regression library to try out
from textwrap import wrap
from datetime import datetime

def plot_prediction_vs_actual(yhat, y, starting_year, file_name, title=''):
        years = [datetime(year=starting_year + i,month=1,day=1) for i in range(0,yhat.shape[0])]
        assert(len(years) == yhat.shape[0] == y.shape[0])
        fig = plt.figure()
        ax = plt.subplot(111)
        ax.plot(years, yhat, 'ro', label='Predicted')
        ax.plot(years, y, 'bo', label='Actual')
        # round to nearest years.
        ax.format_xdata = mdates.DateFormatter('%Y')
        ax.set_ylabel('Anomaly (1901-200 Base Period)')
        ax.set_xlabel('Year')
        ax.legend()
        plt.rcParams['axes.titlepad'] = 20
        plt.rcParams["axes.titlesize"] = 8
        plt.title(title)
        #plt.grid(which='both')
        #plt.title("\n".join(wrap(title,80)))
        #plt.text(0.5, 0.5, "\n".join(wrap(title,80)), fontsize=9)
        fig.savefig(file_name, dpi=fig.dpi)
        plt.close()

# Silence SKlearn warning on python3
def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

ffx_dir = 'data/ffx'
test_X = (pds.read_csv('{}/natural_data_ffx_test_X.csv'.format(ffx_dir)))
test_Y = pds.read_csv('{}/natural_data_ffx_test_Y.csv'.format(ffx_dir))
train_X = (pds.read_csv('{}/natural_data_ffx_train_X.csv'.format(ffx_dir)))
train_Y = pds.read_csv('{}/natural_data_ffx_train_Y.csv'.format(ffx_dir))



# Train over variables found to be correlated with the Granger analysis
group_0 = ['WMGHG', 'Ozone', 'TropAerInd']
group_1 = ['WMGHG', 'Land_Use', 'Ozone', 'TropAerInd']
group_2 = ['WMGHG', 'TropAerDir', 'Ozone', 'TropAerInd']
all_vars = ['WMGHG', 'Ozone', 'Solar', 'Land_Use', 'SnowAlb_BC', \
            'Orbital','TropAerDir','TropAerInd','StratAer']
predictors = group_0
train_X = train_X[predictors]
test_X = test_X[predictors]
# make sure predictors name are for each column are indentical
for i in range(len(predictors)):
    assert(train_X.columns[i] == predictors[i])
    assert(test_X.columns[i] == predictors[i])

data_X = np.append(train_X.to_numpy(), test_X.to_numpy(), axis=0)
data_Y = np.append(train_Y.to_numpy(), test_Y.to_numpy(), axis=0)
# Predict K years ahead
#Ks = [0,1,2,3,4,5,6,7,8,10,9]
Ks = range(1,31)#[15,16,17,18,19,20]
#Ks = [1]
results = {'years_predicted': [], 'test_data_size': [], 'SquaredSumError': [],\
        'MeanAbsError':[], 'RMSError':[], 'Model': []}
data_starting_year = 1880
for K in Ks:
    print('\nModels Predicting {} years ahead:'.format(K))
    # Remove the last K year data from as the Y value is unknown
    cur_data_X = data_X[:len(data_X) - K]
    # Shift Y values K steps up and remove the last K points.
    cur_data_Y = np.roll(data_Y, -K, axis=0)[:len(data_Y) - K]
    train_size = int(cur_data_X.shape[0]*0.8) #80%
    test_starting_year = data_starting_year + (train_size-1) + 1
    print('Data size: {}'.format(cur_data_X.shape[0]))
    print('Test data starting year: {}'.format(test_starting_year))
    # Prepare FFX inputs
    cur_train_X = cur_data_X[:train_size]
    cur_train_Y = cur_data_Y[:train_size]
    cur_test_X = cur_data_X[train_size: ]
    cur_test_Y = cur_data_Y[train_size: ]

    assert(cur_test_X.shape[0] == cur_test_Y.shape[0])
    assert(cur_train_X.shape[0] == cur_train_Y.shape[0])

    print('cur_train_X dim: {}'.format(cur_train_X.shape))
    print('cur_test_X dim: {}'.format(cur_test_X.shape))

    #models = xgp.XGPRegressor()
    #models.fit(train_X.to_numpy(), train_Y.to_numpy())
    models = ffx.run(cur_train_X, cur_train_Y, cur_test_X, \
                 cur_test_Y, predictors)
    best_performing_model={'sq_err':float('inf'), 'model':None}
    for model in models:
        #yhat = model.predict(test_X.to_nump())
        #y = np.reshape(test_Y.to_numpy(), test_Y.to_numpy().shape[0])
        yhat = model.simulate(cur_test_X)
        y = np.reshape(cur_test_Y, cur_test_Y.shape[0])
        print(' * {}'.format(model))
        sq_err = np.sum(np.square(y - yhat))
        print('   squared error= {}'.format(sq_err))
        if sq_err < best_performing_model['sq_err']:
            best_performing_model['model'] = model
            best_performing_model['sq_err'] = sq_err
            best_performing_model['y'] = y
            best_performing_model['yhat'] = yhat
            best_performing_model['rms_err'] = np.sqrt(sq_err/len(yhat))
            best_performing_model['mabs_err'] = np.sum(np.absolute(y - yhat))/len(yhat)

    print('y= {}'.format(best_performing_model['y']))
    print('yhat= {}'.format(best_performing_model['yhat']))
    model = best_performing_model['model']
    results['SquaredSumError'].append(best_performing_model['sq_err'])
    results['RMSError'].append(best_performing_model['rms_err'])
    results['MeanAbsError'].append(best_performing_model['mabs_err'])
    results['test_data_size'].append(len(cur_test_Y))
    results['years_predicted'].append(K)
    results['Model'].append('{}'.format(model))

    #yhat = model.predict(test_X.to_numpy())
    #y = np.reshape(test_Y.to_numpy(), test_Y.to_numpy().shape[0])
    yhat = model.simulate(cur_test_X)
    y = np.reshape(cur_test_Y, cur_test_Y.shape[0])
    plot_prediction_vs_actual(yhat, y, test_starting_year, 'predict_{}_years.png'.format(K),\
            'Predicted years={}'.format(K))
    '''
    FFX = ffx.FFXRegressor()
    FFX.fit(cur_train_X, cur_train_Y)
    #print("Prediction:", FFX.predict(cur_test_X))
    print(" Score(of best performing model):", FFX.score(cur_test_X, cur_test_Y))
    '''
pds.DataFrame(results).to_csv('ffx_results.csv',sep=',', index=False)
print('Done FFX experiment. Check ffx_results.csv for summary and the plots.')


