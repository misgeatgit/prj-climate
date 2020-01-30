import pandas as pds
import numpy as np
import operator
import sys

def feature_percentile(values, N):
    feature_percentile = []
    for i in range(1, N):
        feature_percentile.append(values.quantile(float(i)/N))

    return feature_percentile

# Read 
data = 'data/natural_data.csv'
dataFrame = pds.read_csv(data)
# remove rows with Nan
dataFrame = dataFrame.dropna()
TARGET_CATEGORIES = 10
target_quantiles = feature_percentile(dataFrame['Temperature'], TARGET_CATEGORIES)
# Create the bins
temperature = dataFrame['Temperature'].tolist()
temperature.sort()
Lbound = temperature[0]
Ubound = temperature[len(temperature)-1]
bins = [Lbound] + target_quantiles + [Ubound]
bins.reverse() # Since the predictors are also in reverse order i.e Top10VsOthers...Top90VsOthers instead of the other way round
print('Bins {}'.format(bins))

# read the combined predictor file
combined_predictors_f = sys.argv[1]
df = pds.read_csv(combined_predictors_f, sep=' ')
predicted_temp_values = []
for index, row in df.iterrows():
    prediction = row.values.tolist() #Top10VsOthers, Top20VsOthers....Top90VsOthers
    prediction_cnt = {}
    for i in range(len(prediction)):
        cnt = 0
        for j in range(i+1, len(prediction)):
            if prediction[j] == 1:
                cnt += 1
        prediction_cnt[i] = cnt
        # TODO make sure count is correct
    prediction_cnt = sorted(prediction_cnt.items(), key=operator.itemgetter(1), reverse=True)
    #print(prediction_cnt)
    bin_indexes_to_vote = []
    for i in range(len(prediction_cnt)):
        if i == 0:
            bin_indexes_to_vote.append(prediction_cnt[i][0])
        elif prediction_cnt[i-1][1] == prediction_cnt[i][1]:
            bin_indexes_to_vote.append(prediction_cnt[i][0])
        else:
            break
    values_to_average = [] # If the ensembles doesn't agree, there might be multiple predictions
    for bin_index in bin_indexes_to_vote:
        # average of local Upper and Lower bound
        values_to_average.append((bins[bin_index] + bins[bin_index + 1])/2.0)

    # Average the predictions to a single value
    final_average = sum(values_to_average)/len(values_to_average)
    predicted_temp_values.append(round(final_average,2))

print('TempPredicted {}'.format(predicted_temp_values))
# Rewrite File with the new value
df['PredictedTemperature'] = predicted_temp_values
# Extract lookahead years information
print('Raw Temperature data {} size={}'.format(temperature, len(temperature)))
LA_years = int(combined_predictors_f.split('la')[1].split('all')[0])
print('LA_years {}'.format(LA_years))
for i in range(len(temperature) - LA_years):
    temperature[i] = temperature[i + LA_years]
temperature = temperature[:len(temperature)-LA_years]
test_size = int(len(temperature)*0.2)
#train_size = len(temperature) - test_size
print('Processed Temperature data {} size={}'.format(temperature, len(temperature)))
test_temp = temperature[len(temperature)-test_size:]
print('ActualTemperature {} size={}'.format(test_temp, len(test_temp)))
df['ActualTemperature'] = test_temp # We know we are out of sample testing with the last 26 years
#print ('ActualTemperature {}'.format(df['ActualTemperature']))
df.to_csv(combined_predictors_f, sep=' ', index=False)
