header="bins,train_precision,train_recall,train_accuracy,train_balanced_accuracy,
        test_precision,test_recall,test_accuracy,test_balanced_accuracy,program"
header2="bins,train_recall,train_accuracy,test_recall,test_accuracy,program"
for f in `ls *.csv`; do
	echo $header2 > $f'_tmp'
	cat $f >> $f'_tmp'
	rm $f
	mv $f'_tmp' $f
done

