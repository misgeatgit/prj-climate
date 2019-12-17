bins,train_precision,train_recall,test_precision,test_recall,program

header="bins,train_precision,train_recall,test_precision,test_recall,program"

for f in `ls`; do
	echo $header > $f'_tmp'
	cat $f >> $f'_tmp'
	rm $f
	mv $f'_tmp' $f
done

