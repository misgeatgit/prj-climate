#!/bin/python2.7

import os
import csv
import argparse


EVAL_TABLE_PATH="/usr/local/bin/eval-table"
OUT = 'Temperature'
def parse_output(outputf,combof):
	"""Extract the combo programs from a given moses output file
	params:
	moses output file,combo file to be saved
	"""	
	f = open(outputf,'r')
	combo_line = f.readline()
	f.close()
	combo = combo_line.split(' ',1)[1]
	combo_file = open(combof,'w')
	combo_file.write(combo)
	combo_file.close()	
		
def eval_output(ifile,cfile,ofile):
	"""evaluate the combo program
	params:
	actual file,combo file,output file"""
        print('Evaluating {}'.format(ifile))
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
def get_recall(predictedf,actualf):
	"""recall for fixed train test"""
	actual_values = values_of_col(actualf,OUT)
	predicted_values = values_of_col(predictedf,OUT)
	true_positve=0.0
	trues=0.0
	assert len(actual_values) == len(predicted_values)
	for i in range(0,len(actual_values)):
		if actual_values[i] == '1':
			trues += 1.0
			if predicted_values[i] == '1':
				true_positve += 1.0
	#print "TRUES=%s TRUE_POSITIVE=%s"%(str(trues),str(true_positve))
	rounded_recall = true_positve/trues
	return round(rounded_recall,4)	
def get_precision(predictedf,actualf):
	"""precision for fixed train test"""
	actual_values = values_of_col(actualf,OUT)
	predicted_values = values_of_col(predictedf,OUT)
	true_positve = 0.0
	positive = 0.0
	assert len(actual_values) == len(predicted_values)
	for i in range(0,len(actual_values)):
		if predicted_values[i] == '1':
			positive += 1.0
			if actual_values[i] == '1':
				true_positve += 1.0
	rounded_prec = true_positve/positive			
	return round(rounded_prec,4)
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
		combof = os.path.join(combofp_dir,"%s.combo"%(mtrainfname))
		parse_output(moses_resf,combof)
		mtrain_evalf = os.path.join(trtstdir,mtrainfname+".eval")
		mtest_evalf = os.path.join(trtstdir,mtestfname+".eval")
		#start
		eval_output(os.path.join(trtstdir,mtrainfname),combof,mtrain_evalf)
		eval_output(os.path.join(trtstdir,mtestfname),combof,mtest_evalf)
		mtrain_prec = get_precision(mtrain_evalf,os.path.join(trtstdir,mtrainfname))
		mtrain_rec = get_recall(mtrain_evalf,os.path.join(trtstdir,mtrainfname))
		mtest_prec = get_precision(mtest_evalf,os.path.join(trtstdir,mtestfname))
		mtest_rec = get_recall(mtest_evalf,os.path.join(trtstdir,mtestfname))
                #result_file = os.path.join(os.path.split(trtstdir)[0],"results.csv")
                result_file = trtstdir+"/results.csv"
                print('Saved result to {}'.format(result_file))
		save_result([mtrain_prec,mtrain_rec,mtest_prec,mtest_rec],result_file)	   	
                # Append result of this experiment to results.csv
                os.popen('rm resluts/* -rf')
                all_results = 'results/look_ahead{}_results.csv'
                f = open(combof,'r')
	        combo = f.readline()
	        f.close()
                exp = os.path.split(trtstdir)
                exp = exp[len(exp)-1]
                print("Experiment dir {}".format(exp))
                #'exp_b*la*'
                bins_la = exp[5:].split('la')
                bins = int(bins_la[0])
                la = int(bins_la[1])
                with open(all_results.format(la), 'a+') as f:
                    line = '{},{},{},{},{},{}'.format(bins,mtrain_prec,mtrain_rec,mtest_prec,mtest_rec,combo)
                    f.write(line)
	else:
		parser.print_help()   
