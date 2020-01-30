
echo "Preparing Binarized data for MOSES"
python generate_MOSES_training_data.py
echo "Running Moses"
sh run_anal.sh
echo "Merging Predictor model outputs on test"
python merge_predictors.py
echo "Done"
echo "MOSES approximate Floating value prediction via voting"
#sh vote.sh
