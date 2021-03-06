#!/bin/python2.7

import os
import csv
import argparse


EVAL_TABLE_PATH="/usr/local/bin/eval-table"
OUT = 'Temperature'
def extract_programs(outputf):
	"""Extract the combo programs from a given moses output file
	params:
	moses output file
        return list of string representation of the programs
	"""	
        programs = []
        with open(outputf,'r') as f:
	    combo_lines = f.readlines()
            for combo_line in combo_lines:
                 combo = combo_line.split(' ',1)[1]
	         programs.append(combo)
        return programs

def eval_output(ifile,cfile,ofile):
	"""evaluate the combo program
	params:
	actual file,combo file,output file"""
        print('Evaluating {} on combo {}'.format(ifile, cfile))
	global EVAL_TABLE_PATH
	EVAL_TABLE_ARGS = " -i %s -C %s -o %s -u %s "%(ifile,cfile,ofile,OUT)
	result=os.system(EVAL_TABLE_PATH + " " + EVAL_TABLE_ARGS) 
	if result!=0:
		print "error while executing"
		exit(0)	

def values_of_col(csvf,col_name,sepchar=' '):
	"""get values of a given column name from a csv file
	returns list of the column values without the column name
	params csv file path,column name,delimiter char in the csv
	"""
	col_values=[]
	with open(csvf,'rb') as f:
		reader=csv.reader(f,delimiter=sepchar)
		csv_list=list(reader)
		header_row=csv_list[0]		
		col_name_index=header_row.index(col_name)
		for row in csv_list:
			col_values.append(row[col_name_index])
	del col_values[0] # remove the column name		
	return col_values						
def calc_performance(predicted, actual):
    assert len(predicted) == len(actual)
    #print('Actual,Predicated values {}'.format(zip(predicted, actual)))
    tp = tn = fp = fn = 0.0       #tp - true positive tn -true negative fp - false positive fn -false negative
    for i in range(0, len(predicted)):
        if predicted[i] == '1':
            if actual[i] == '1':
                tp += 1.0
            else:
                fp += 1.0
        else:
            if actual[i] == '0':
                tn += 1.0
            else:
                fn += 1.0

    return {'precision':tp/(tp + fp) if tp+fp > 0 else -1, 'recall':tp/(tp + fn) if tp + fn > 0 else -1, \
            'accuracy':(tp + tn)/(tp + tn + fp + fn), \
            'balanced_accuracy':(tp/(tp + fn) + tn/(tn + fp))/2 if tp+fp > 0 and tn+fp > 0 else -1}

def save_result(data,resultf):
	#print "RESULT FILE:%s"%resultf
	header=["train_precision","train_recall","test_precision","test_recall"]
	result_csv=[header,data]
	resultf=open(resultf,"wb")
	writer=csv.writer(resultf)
	writer.writerows(result_csv)
if __name__ == "__main__":
	print "parsing...evaluatin...scoring"
	usage = "usage: %prog [options]\n"
	parser = argparse.ArgumentParser(usage)
	parser.add_argument("-T", "--trainf",nargs=1,help = "moses training file")
	parser.add_argument("-t", "--testf",nargs=1,help = "moses testing file")
	parser.add_argument("-d", "--trtstdir",nargs=1,help = "moses training test and evaluation output file dir")
	parser.add_argument("-c", "--combof",nargs=1,help = "file where combo program is within")
	args = parser.parse_args()
	if args.trainf and args.testf and args.trtstdir and args.combof:
                # Training and testing files
                mtrainfname = args.trainf[0]
                mtestfname = args.testf[0]
		
                trtstdir = os.path.abspath(args.trtstdir[0]) # a dir to store eval-table output
		moses_resf = os.path.abspath(args.combof[0]) #
		combofp_dir = os.path.split(moses_resf)[0]
		programs = extract_programs(moses_resf)
                i = 0
                result = ''
                suffix = ''
                exp_result_dir = ''
                for program in programs:
		    combof = os.path.join(combofp_dir,"{}_{}.combo".format(mtrainfname, i))
		    mtrain_evalf = os.path.join(trtstdir,'{}_{}.eval'.format(mtrainfname, i))
		    mtest_evalf = os.path.join(trtstdir,'{}_{}.eval'.format(mtestfname, i))
                    i += 1
		    # Create a file containing the combo program
                    with open(combof, 'w') as f:
                        f.write(program)
                    # Run eval-table
		    eval_output(os.path.join(trtstdir,mtrainfname), combof, mtrain_evalf)
		    eval_output(os.path.join(trtstdir,mtestfname), combof, mtest_evalf)

                    ptr = calc_performance(values_of_col(mtrain_evalf, OUT), \
                            values_of_col(os.path.join(trtstdir,mtrainfname), OUT))
                    ptst = calc_performance(values_of_col(mtest_evalf, OUT), \
                            values_of_col(os.path.join(trtstdir,mtestfname), OUT))

                    # Append result of this experiment to results.csv
                    exp = os.path.split(trtstdir)
                    pdir = os.path.split(exp[0])[1]
                    bins_la = pdir.split('la')
                    la = int(bins_la[1])
                    bins = int(bins_la[0][5:])
	            combo = program
                    line = '{},{},{},{},{},{}'.format(bins, ptr['recall'],\
                            ptr['accuracy'],ptst['recall'],ptst['accuracy'],combo)
                    # Append to result
                    result += line
                    suffix = pdir+'_'+exp[1]
                    exp_result_dir='results/LA{}'.format(la)
                if not os.path.isdir(exp_result_dir):
                    os.mkdir(exp_result_dir)
                result_f = '{}/{}_results.csv'.format(exp_result_dir, suffix)
                with open(result_f, 'a+') as f:
                    f.write(result)
                print('Result saved to {}'.format(result_f))
	else:
	    parser.print_help()
