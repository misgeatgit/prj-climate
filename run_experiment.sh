
echo "Preparing Binarized data for MOSES"
python generate_MOSES_training_data.py
echo "Running Moses"
sh run_anal.sh
echo "Done"
