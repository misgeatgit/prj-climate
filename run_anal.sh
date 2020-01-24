for exp_on_lookahead in `ls exp`; do
	for exp_on_target in `ls exp/$exp_on_lookahead`; do
		DIR=exp/$exp_on_lookahead/$exp_on_target
		for csv in `ls $DIR/*.csv`; do
			train_file=$DIR/exp_train.csv
			test_file=$DIR/exp_test.csv
			# Create test(~20%) and train(~80%) data from the original
			head -n1 $csv > $test_file #add header
			tail -n26 $csv >> $test_file #
			head -n106 $csv > $train_file
			# Run MOSES on the training data
			combof=exp/$exp_on_lookahead/$exp_on_target/combo.txt
			echo 'Running MOSESE on '$csv
			moses -H it -u Temperature -W1  -i \
				$train_file \
				--diversity-autoscale=1 --diversity-pressure=0.0 \
				--complexity-ratio=3 --complexity-temperature=5 \
				> $combof
			echo 'Done running MOSES now Running anal.py'
			# Run performance measurement tool script.
			python anal_exp.py -t exp_test.csv -T exp_train.csv \
			--trtstdir $DIR --combof $combof
			echo 'Done analyzing.'
		done
	done
done

