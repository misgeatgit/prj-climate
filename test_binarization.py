import pandas as pds
from generate_MOSES_training_data import feature_percentile, binarize


xdf = pds.DataFrame({'nums': [i for i in range(0,11)]})

expected = [2.0, 4.0, 6.0, 8.0]

# Get quantiles for 5 bin i.e (0,5)
percentile = feature_percentile(xdf['nums'], 5)

assert(percentile == expected)

assert( binarize(1, percentile, 5) == [1,0,0,0,0])
assert( binarize(2, percentile, 5) == [1,0,0,0,0])
assert( binarize(5, percentile, 5) == [0,0,1,0,0])
assert( binarize(11, percentile, 5) == [0,0,0,0,1])
assert( binarize(8, percentile, 5) == [0,0,0,1,0])
