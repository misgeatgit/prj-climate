
echo 'Appending Floating value ensemble model prediction'
for csv in `ls results/*.csv`; do python vote.py $csv; done
echo 'Done'
