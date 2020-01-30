
# Create test(~20%) and train(~80%) data from the original
GET_TRAIN_TEST_SIZE_PY=$(cat <<END
# python code starts here
import sys
import pandas as pds

file = sys.argv[1]
#LA_years = int(file.split('LookAhead')[1].split('_Top')[0])
df = pds.read_csv(file)
size = df.shape[0]
test_size = int(size*0.2)
train_size = size - test_size
print('{},{}'.format(train_size,test_size))
#python code Ends here
END
)

for exp_on_lookahead in `ls exp`; do
	for exp_on_target in `ls exp/$exp_on_lookahead`; do
		DIR=exp/$exp_on_lookahead/$exp_on_target
		for csv in `ls $DIR/*.csv`; do
			echo 'Working with:'$csv
			res="$(python -c "$GET_TRAIN_TEST_SIZE_PY" $csv)"
			IFS=', ' read -r -a array <<< "$res"
			echo "train_test size: ${array[0]},${array[1]}"
			train_file=$DIR/exp_train.csv
			test_file=$DIR/exp_test.csv
			head -n${array[0]} $csv > $train_file
			head -n1 $csv > $test_file #add header
			tail -n${array[1]} $csv >> $test_file #
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

