import pandas as pds
import sys
from os import listdir
from os.path import isfile, join

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
        features = extract_feature_names(program_str)
        for feature in features:
            if feature in counts.keys():
                counts[feature] += 1
            else:
                counts[feature] = 1
    return counts

#exp_dir = '/home/misgana/Desktop/prj-climate/results/LA0' #argv[1] #director where CSV file is located.
exp_dir = sys.argv[1] #director where CSV file is located.
csv_files = [f for f in listdir(exp_dir) if isfile(join(exp_dir, f))]
print csv_files
count_table = {}
for csv_file in csv_files:
    df = pds.read_csv(join(exp_dir, f))
    programs = []
    for program in df['program']:
        programs.append(program.strip())
    counts = count_feature_appearance(programs)
    model_name = 'Top'+ csv_file.split('VsOthers')[0].split('_Top')[1] + 'VsOthers'
    count_table[model_name] = counts


features = []
count_table_df = {}
for model_name in count_table:
    count_table_df[model_name] = []
    for feature in counts:
        if feature not in features:
            features.append(feature)
count_table_df['Features'] = features

for feature in features:
    for model_name in count_table:
        count_table_df[model_name].append(count_table[model_name][feature])

df = pds.DataFrame(count_table_df)
df.to_csv(join(exp_dir, 'feature_counts.csv'), sep=',', index=False)
print(df)


