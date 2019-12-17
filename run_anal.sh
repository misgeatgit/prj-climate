
for exp in `ls exp`; do
	for csv in `ls exp/$exp`; do
		file=exp/$exp/$csv
		echo 'Running MOSESE on '$file
		moses -H it -u Temperature -W1  -i \
			$file \
		       	--diversity-autoscale=1 --diversity-pressure=0.0 \
			--complexity-ratio=3 --complexity-temperature=5 \
			> exp/$exp/combo.txt
		echo 'Done running MOSES now Running anal.py'
		head -n1 $file > exp/$exp/exp_test.csv
		tail -n26 $file >> exp/$exp/exp_test.csv
		head -n106 $file > exp/$exp/exp_train.csv
		python anal_exp.py -t exp_test.csv -T exp_train.csv \
			--trtstdir exp/$exp --combof exp/$exp/combo.txt
		echo 'Done analyzing.'
	done
done

