

import os
import pandas as pds
import numpy as np
'''
   Current directory hierarchy of the exp dir looks like the following:
   exp
    |
    exp1
     |
     1Quartile
     2Quartiel
     .
     .
    exp2
    .
    .
'''

EXP_DIR =  'exp'
DUMP_DIR = 'results'
TARGET = 'Temperature'
TEST_DATA_FILE_NAME = 'exp_test.csv'
EVAL_OUTPUT_FILE_NAME = 'exp_test.csv.eval'

forecasting_exp_dirs = os.listdir(EXP_DIR)
merged_predictors =  {}
for forecasting_exp_dir in forecasting_exp_dirs:
    forecasting_exp_dir_abspath = os.path.abspath(EXP_DIR+'/'+forecasting_exp_dir)
    predictor_exp_dirs = os.listdir(forecasting_exp_dir_abspath)
    #append predictor names as columns
    for predictor_exp_dir in predictor_exp_dirs:
        abspath = forecasting_exp_dir_abspath+'/'+predictor_exp_dir
        eval_f = abspath+'/'+EVAL_OUTPUT_FILE_NAME
        # Name column with same name as the predictor dir name
        merged_predictors[predictor_exp_dir] = pds.read_csv(eval_f, sep=' ')[TARGET].values
    # Dump the table to a csv file with the same name as the forecasting_exp_dir
    pds.DataFrame(merged_predictors).to_csv(DUMP_DIR+'/'+forecasting_exp_dir+'all_predictors_result.csv', sep=' ', index=False)


