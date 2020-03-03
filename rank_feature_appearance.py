import pandas as pds
import sys
from os import listdir
from os.path import isfile, join
from sets import Set

def extract_feature_names(x):
    i = 0
    feature_names = []
    while i < len(x):
        start = i + 1
        if x[i] == '$':
            while i < len(x) and (x[i] != ' ' and x[i] != ')'):
                i += 1
            #print('Extracting substring [{},{}]'.format(start,i+1))
            MOSES_feature = x[start:i]
            feature_name = MOSES_feature.split('_bin')[0]
            feature_names.append(feature_name)
            #print(feature_name)
        i += 1

    return feature_names

def count_feature_appearance(programs):
    counts = {}
    for program_str in programs:
        #print('Program: {}'.format(program_str))
        features = extract_feature_names(program_str)
        #print('Features: {}'.format(features))
        for feature in features:
            if feature in counts:
                counts[feature] += 1
            else:
                counts[feature] = 1
    return counts

#exp_dir = '/home/misgana/Desktop/prj-climate/results/LA0' #argv[1] #director where CSV file is located.
exp_dir = sys.argv[1] #director where CSV file is located.
csv_files = [f for f in listdir(exp_dir) if isfile(join(exp_dir, f))]
count_table = {}
for csv_file in csv_files:
    print(csv_file)
    df = pds.read_csv(join(exp_dir, csv_file))
    programs = []
    for program in df['program']:
        programs.append(program.strip())
    counts = count_feature_appearance(programs)
    model_name = 'Top'+ csv_file.split('VsOthers')[0].split('_Top')[1] + 'VsOthers'
    #print('Counts: {}'.format(counts))
    count_table[model_name] = counts

# Prepare a DataFrame for counts of each feature in each Model
count_table_df = {}

# Get all feature names
features = Set()
for model_name in count_table:
    for feature in count_table[model_name]:
            features.add(feature)
count_table_df['Features'] = list(features)

# Fill counts of each feature in each model
for model_name in count_table:
    count_table_df[model_name] = []
    for feature in features:
        if feature in count_table[model_name]:
            count_table_df[model_name].append(count_table[model_name][feature])
        else:
            count_table_df[model_name].append(0)

df = pds.DataFrame(count_table_df)
# Total counts
df['Total']=df.sum(axis=1)
df = df.sort_values(by='Total', ascending=False)
# Save 
df.to_csv(join(exp_dir, 'feature_counts.csv'), sep=',', index=False)
print(df)


