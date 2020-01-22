import pandas as pd
import numpy as np
import os.path
import collections

csvarray = pd.read_csv("my.csv")
i = 0

for line in csvarray.values:
    print("### LINE %d" % i)
    i=i+1
    for chunk in line:
        print("-- %s --" % chunk)


