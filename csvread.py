import pandas as pd
import numpy as np
import os.path
import collections

csvarray = pd.read_csv("my.csv")
i = 0

# single line comment
'''
multiline comment
'''

# print line-wise contents of csv file
for line in csvarray.values:
    if i==0:
        print("skipping first line...")
    else:
        print("processing line %d" % i)
        voltage = float(line[2])
        print("  --> V=%f" % voltage)
    i += 1
    


# let's see what pandas.cut() has in store for us



