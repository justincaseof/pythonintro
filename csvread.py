import pandas as pd
import numpy as np
import os.path
import collections
import functools
import statistics

csvarray = pd.read_csv("my.csv")
i = 0

# single line comment
'''
multiline comment
'''

# deviation in percent to identify coherent voltages
deviationpercentage = 15

# temp variables
previous = None
sliceindex = 0
slices = []

# print line-wise contents of csv file
for line in csvarray.values:
    if i==0:
        print("skipping first line since these are the CVS labels...")
    else:
        print("processing line %d" % i)
        # get the voltage
        voltage = float(line[2])

        # init list if neccesary
        if slices.__len__() <= sliceindex:
            slices.append([])

        # calculate current mean
        numberOfSliceValues = slices[sliceindex].__len__()
        if numberOfSliceValues > 0:
            '''
            # OPTION 1: calc sum
            _sum = 0
            for _voltage in slices[sliceindex]:
                _sum += _voltage
            currentMean = _sum / numberOfSliceValues
            '''

            '''
            # OPTION 2: calc sum
            _sum = functools.reduce(lambda a, b: a + b, slices[sliceindex])
            currentMean = _sum / numberOfSliceValues
            '''

            # OPTION 3: python 3 statistics
            currentMean = statistics.mean(slices[sliceindex])

            # calculate deviation of current value

            diff = abs(voltage - currentMean)
            currentDeviationPercentage = diff / currentMean * 100

            print('  --> mean={0:.2f} :: V={1} :: deviation={2:.2f}%'.format(currentMean, voltage, currentDeviationPercentage))

            if currentDeviationPercentage > deviationpercentage:
                print("!!! found beginning of new slice")
                slices.append([])
                sliceindex += 1

        # add current value to current slice
        slices[sliceindex].append(voltage)
    i += 1

# let's see what pandas.cut() has in store for us
print("\nResult\n-----")
print("We found {0} lists".format(slices.__len__()))
idx = 0
for _sublist in slices:
    print("  --> list {0} has {1} entries and a mean of {2}".format(idx, _sublist.__len__(), statistics.mean(_sublist)))
    idx += 1

