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

# deviation in percent to identify coherent voltages
deviationpercentage = 20

# temp variables
base = 0
sliceindex = 0

slices=[]


# print line-wise contents of csv file
for line in csvarray.values:
    if i==0:
        print("skipping first line...")
    else:
        print("processing line %d" % i)
        voltage = float(line[2])
        print("  --> V=%f" % voltage)
        if base*100/voltage > deviationpercentage:
            print("!!! found beginning of new slice")
            base = voltage
            slices[sliceindex] = []
            sliceindex += 1
            # add current value
            slices[sliceindex].append(voltage)
    i += 1
    


# let's see what pandas.cut() has in store for us



