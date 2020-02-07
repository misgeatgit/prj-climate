
for dir in `ls -d */`; do
	#mkdir $dir/tmp1 && mv $dir/exp_b8*.csv  $dir/tmp1;
	#mkdir $dir/tmp && mv $dir/*.csv $dir/tmp;
	#mv $dir/tmp1/*.csv $dir/ && rm $dir/tmp1/ -r;
	rm $dir"tmp1" -r;
	#mv $dir"tmp/exp_b8*.csv" $dir;
done
