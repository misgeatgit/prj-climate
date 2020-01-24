#!/usr/bin/env python
# coding: utf-8

# In[64]:


import os
import pandas as pds
# Params to experiment with
# bin size
quantiles = [8]#range(5,11)
# Window size
K = [1]#range(5,11) # Window size between 5years and 10years
smoothing_method = ['MA', 'MV', 'HE'] # Moving Average, Moving Variance and Hurst Exponent
LOOK_AHEAD_YEARS = [0,1,2,3,4,5,6,7,8,9,10]

def feature_percentile(values, N):
    feature_percentile = []
    for i in range(1, N):
        feature_percentile.append(values.quantile(float(i)/N))

    return feature_percentile

# Test this there are missing values in the raw data.
def binarize(value, percentile, N):
    if len(percentile) != N - 1:
        print("Error: There should be exactly N-1 list of percentiles for N bins. \
               Length of percentiles provided is {} and Bin size is {}".format(len(percentile), N))
        exit()
    bit_array =[0] * N
    for i in range(0, len(percentile)):
        if value <= percentile[i]:
            bit_array[i] = 1
            break
        if i == len(percentile)-1 and value > percentile[i]:
            bit_array[i + 1] = 1
    if 1 not in bit_array:
        print('Error: there should be 1 in the bit array. value {}  percentile {} N{}'.format(value, percentile, N))
    return bit_array

feature_names= ['WMGHG', 'Ozone', 'Land_Use', 'TropAerDir', 'TropAerInd', # Anthropogenic variables
               'Solar', 'SnowAlb_BC', 'Orbital', 'StratAer',       # Natural variables
               'Temperature', 'Ocean'] # Target variables

data = 'data/natural_data.csv'
dataFrame = pds.read_csv(data)

# remove rows with Nan
dataFrame = dataFrame.dropna()

#2. Choosing a certain window size K,
#  Apply Moving Average or Moving Variance or Hurst exponent to each 
# feature let the new Feature be called Ft
os.popen('rm exp/* -rf')
for K_exp in K:
    for LOOK_AHEAD_YEAR in LOOK_AHEAD_YEARS:
        for Q_exp in quantiles:
            smoothing = smoothing_method[0]
            transformed_data= {}

            for i in range(0, len(feature_names)-2):
                feature_rolling = dataFrame[feature_names[i]].rolling(K_exp)
                smoothed_feature = None
                if smoothing == 'MA':
                    smoothed_feature = feature_rolling.mean()
                elif smoothing == 'MV':
                    smoothed_feature = feature_rolling.var()
                elif smoothing == 'MV':
                    smoothed_feature = feature_rolling.mean() #Change this wit Hurst exponent method
                else:
                    print("Unknown smoothing method({}) provided. Exiting.".format(smoothing))
                    exit()

                transformed_data[feature_names[i]] = smoothed_feature
                #WMGHG_MV = WMGHG_rolling.var()

            # Build a dataFrame
            transformed_df = pds.DataFrame(transformed_data) 
            transformed_df = transformed_df.dropna()

            #3. calculate the Nth percentile(i.e quantile normalization) for each feature 
            # where Nth a paramenter to experiment with based on quantile thus feature
            # will be converted into N bits 
            # i.e Fti_bin1....Fti_binN where Fti is the ith feature.

            binarized_data = {}
            for feature_name in transformed_df:
                #print('Feature_name: {}'.format(feature_name))
                values = transformed_df[feature_name]
                percentile = feature_percentile(values, Q_exp)
                for value in values:
                    bits = binarize(value, percentile, Q_exp)
                    #print("Binarize({}) = {}".format(value, bits))
                    for i in range(0, len(bits)):
                        key = '{}_bin{}'.format(feature_name, i)
                        if key in binarized_data.keys():
                            binarized_data[key].append(bits[i])
                        else:
                            binarized_data[key] = [bits[i]]

            exp_dir = 'exp/exp_b{}la{}'.format(Q_exp, LOOK_AHEAD_YEAR)
            os.mkdir(exp_dir)

            # Convert target featuren in to UP(1) and DOWN(0)
            # by using quantiles as border values.
            targets = []
            TARGET_CATEGORIES = 10
            target_quantiles = feature_percentile(dataFrame['Temperature'], TARGET_CATEGORIES)
            for tq in target_quantiles:
                target_vec = []
                for t in dataFrame['Temperature']:
                    if t < tq:
                        target_vec.append(0)
                    else:
                        target_vec.append(1)
                targets.append(target_vec)

            # Predict $LOOK_AHEAD_YEAR ahead
            quartile = 1
            for target_vec in targets:
                look_ahead = []
                for i in range(0, len(target_vec) - LOOK_AHEAD_YEAR):
                    look_ahead.append(target_vec[i + LOOK_AHEAD_YEAR])

                target_df = pds.DataFrame({'Temperature':look_ahead})
                features_df = pds.DataFrame(binarized_data)
                # Resize
                features_df.drop(features_df.tail(LOOK_AHEAD_YEAR).index,inplace=True)
                # Append target
                features_df['Temperature'] = look_ahead

                # Dump dataFrame to CSV file
                target_exp_dir = '{}/{}Quartile'.format(exp_dir, quartile)
                os.mkdir(target_exp_dir)
                PATH = '{}/natural_data_MOSES_Bins{}_LookAhead{}_{}Quartile.csv'.format(target_exp_dir, Q_exp, LOOK_AHEAD_YEAR, quartile)
                quartile += 1
                features_df.to_csv(PATH, sep=' ', index=False)
