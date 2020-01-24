import pandas as pd
import numpy as np
import os.path
import collections
import functools
import statistics
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import time

''' 
CONSTANTS
'''
# CSV row labels
LABEL_01_time = 'time (UTC)'
LABEL_02_tanDelta = 'tan delta'
LABEL_03_Vrms = 'test object RMS voltage (V)'
LABEL_04_current = 'test object current (I)'
LABEL_05_frequency = 'input frequency (Hz)'
LABEL_06_capacitance = 'test object capacitance (F)'

# deviation in percent to identify related entries
MAX_deviationPercentage = 15

'''
FUNCTION DEFs
'''

def my_mean(rows):
    result = 0
    for _current_row in rows:
        result += _current_row[LABEL_03_Vrms]
    return result / rows.__len__()

def split_CSV_to_DataFrames(fileName: 'my.csv'):
    '''
    VARS
    '''
    # result vars
    sliceIndex = 0
    slices = [[]]   # yes, initialize with an empty first list

    # ingest CSV
    allDataAsDict = pd.read_csv(fileName,
                          header=None,
                          skiprows=2,
                          names=[LABEL_01_time,
                                 LABEL_02_tanDelta,
                                 LABEL_03_Vrms,
                                 LABEL_04_current,
                                 LABEL_05_frequency,
                                 LABEL_06_capacitance]
                                )

    for _num, _row in allDataAsDict.iterrows():
        # do we already have some values?
        _slice_len = slices[sliceIndex].__len__()
        if _slice_len > 0:
            currentMean = my_mean(slices[sliceIndex])
            currentValue = _row[LABEL_03_Vrms]

            # calculate deviation of current value to our current mean value
            diff = abs(currentValue - currentMean)
            currentDeviationPercentage = diff / currentMean * 100

            print('--> mean={0:.2f} :: V={1} :: deviation={2:.2f}%'
                  .format(currentMean, currentValue, currentDeviationPercentage))

            # are we still in our range?
            if currentDeviationPercentage > MAX_deviationPercentage:
                # we found a value which exceeds our maximum tolerated deviation.
                # thus, we assume the beginning of a new time line.
                sliceIndex += 1
                slices.append([])
                print("[+] found beginning of new slice. adding list #{}".format(sliceIndex))

        print("  [+] Adding row with Voltage {:.2f} to list #{}".format(_row[LABEL_03_Vrms], sliceIndex))
        slices[sliceIndex].append(_row)

    return slices


### RUN ###

# create our list.
lists = split_CSV_to_DataFrames("my.csv")

print("\nResult\n-----")
print("We found {0} lists".format(lists.__len__()))
idx = 0
for _sublist in lists:
    print("  --> list {0} has {1} entries".format(idx, _sublist.__len__()))
    idx += 1

    # we need to convert to dataframe first...
    _frame = pd.DataFrame.from_records(_sublist)

    # now we have our timeseries for current iteration.
    frequencies = _frame[LABEL_05_frequency]
    tanDeltas = _frame[LABEL_02_tanDelta]

    # provide our values to plot lib
    plt.plot(frequencies, tanDeltas)
    plt.xlabel(LABEL_05_frequency, fontsize=10)
    plt.ylabel(LABEL_02_tanDelta, fontsize=10)
    plt.xscale("log")

# finally, plot all graphs into one diagram and give the file a proper name.
plt.savefig("{}_mygraph_{}-series.png".format(int(time.time()), idx))


