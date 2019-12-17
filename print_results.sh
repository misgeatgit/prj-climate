for expdir in `ls exp`; do
	echo 'Results of '$expdir
	cat exp/$expdir/results.csv
done
