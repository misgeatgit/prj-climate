 for dir in `ls -d results/*/`; do 
	 rm $dir"feature_counts.csv"; 
	 python rank_feature_appearance.py $dir;
 done
