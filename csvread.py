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


def my_mean(rows, rowLabel):
    result = 0
    for _current_row in rows:
        result += _current_row[rowLabel]
    return result / rows.__len__()

def createMean(_sourcerow, _meanVrms):
    _new_row = {
        LABEL_01_time: _sourcerow[LABEL_01_time],
        LABEL_02_tanDelta: _sourcerow[LABEL_02_tanDelta],
        LABEL_03_Vrms: _meanVrms,
        LABEL_04_current: _sourcerow[LABEL_04_current],
        LABEL_05_frequency: _sourcerow[LABEL_05_frequency],
        LABEL_06_capacitance: _sourcerow[LABEL_06_capacitance]
    }
    return _new_row

def split_CSV_to_DataFrames(fileName):
    '''
    VARS
    '''
    # result vars
    sliceIndex = 0
    slices = [[]]  # yes, initialize with an empty first list

    '''
    an inner function. yikes!
    '''
    def snapshotAndAddCurrentMean():
        # take timestamp
        _sourcerow = _current_vals[0]
        _meanTanD = my_mean(_current_vals, LABEL_02_tanDelta)
        _new_row = {
            LABEL_01_time: _sourcerow[LABEL_01_time],
            LABEL_02_tanDelta: _meanTanD,
            LABEL_03_Vrms: _sourcerow[LABEL_03_Vrms],
            LABEL_04_current: _sourcerow[LABEL_04_current],
            LABEL_05_frequency: _sourcerow[LABEL_05_frequency],
            LABEL_06_capacitance: _sourcerow[LABEL_06_capacitance]
        }

        #slices[sliceIndex].append(pd.DataFrame.from_records([_new_row]))
        slices[sliceIndex].append(_new_row)

        print("  [+] added mean of tanD={} for frequency {}".format(_meanTanD, _curr_freq))

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
    _current_vals = []
    _curr_freq = None
    for _num, _row in allDataAsDict.iterrows():
        _freq = round(_row[LABEL_05_frequency])

        _slice_len = slices[sliceIndex].__len__()
        if _slice_len > 0:
            currentMean = my_mean(slices[sliceIndex], LABEL_03_Vrms)
            currentValue = _row[LABEL_03_Vrms]

            # calculate deviation of current value to our current mean value
            diff = abs(currentValue - currentMean)
            currentDeviationPercentage = diff / currentMean * 100

            print('--> mean={0:.2f} :: f={1}, V={2} :: deviation={3:.2f}%'
                  .format(currentMean, _freq, currentValue, currentDeviationPercentage))

            # are we still in our range?
            if currentDeviationPercentage > MAX_deviationPercentage:
                # prior to starting new slice, we need to add current values. no matter what.
                # CALC AVERAGE AND ADD TO LIST
                if len(_current_vals) > 0:
                    snapshotAndAddCurrentMean()
                # reset
                _current_vals = []
                _curr_freq = None

                # we found a value which exceeds our maximum tolerated deviation.
                # thus, we assume the beginning of a new time line.
                sliceIndex += 1
                slices.append([])

                print("[+] found beginning of new slice. adding list #{}".format(sliceIndex))

        # check for coherent frequencies
        if _curr_freq is None:
            # first value
            _curr_freq = _freq
            _current_vals.append(_row)

            print("  [+] new frequency range: {}".format(_curr_freq))
        else:
            # check if we're still in range. we assume zero tolerance (except deviation due to previous rounding)
            if _freq == _curr_freq:
                _current_vals.append(_row)
            else:
                # CALC AVERAGE AND ADD TO LIST
                snapshotAndAddCurrentMean()

                # reset
                _current_vals = []

                _curr_freq = _freq
                # new row to empty list of new frequency
                _current_vals.append(_row)

                print("  [i] new frequency range: {}".format(_curr_freq))

    # CALC AVERAGE AND ADD TO LIST
    snapshotAndAddCurrentMean()

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
    currentMean = my_mean(_sublist, LABEL_03_Vrms)
    currentMean_rounded = int(currentMean / 100) * 100
    print("  --> mean Vrms is {}".format(currentMean))
    print("  --> rounded Vrms is {}".format(currentMean_rounded))

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


