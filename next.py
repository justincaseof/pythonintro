# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 10:28:45 2020

@author: sarah
"""

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

#%matplotlib qt

mycsvdatei1= "to04_LCDI_0203_fixed.csv"
label1 = "Erde, korrekt "
color1 = "#00008B"

# =============================================================================
# mycsvdatei2= r"C:\Users\sarah\OneDrive\Documents\Uni\Diplomarbeit\3-Daten\2-Versuche\2-Hauptversuche\KW9\to07_Erde_SRincorrect_Omicrom_2802.csv"
# label2= "Erde, inkorrekt"
# color2 = "#00CD00"
#
# mycsvdatei3= r"C:\Users\sarah\OneDrive\Documents\Uni\Diplomarbeit\3-Daten\2-Versuche\2-Hauptversuche\KW9\to07_ohneErde_SRincorrect_Omicrom_2802.csv"
# label3= "ohne Erde, inkorrekt"
# color3 = "#8B2E2F"
#
# mycsvdatei4= r"C:\Users\sarah\OneDrive\Documents\Uni\Diplomarbeit\3-Daten\2-Versuche\2-Hauptversuche\KW9\to07_ohneErde_SRcorrect_Omicrom_2802.csv"
# label4= "ohne ERde, korrekt"
# color4 = "#CD2990"
# =============================================================================

fig, ax = plt.subplots(figsize=(8, 6))
sns.set()
sns.set(style='ticks', palette='Set1',font='Open Sans')

'''
CONSTANTS
'''
# CSV row labels
LABEL_01_time = 'Zeit'
LABEL_02_frequency = 'Frequenze [Hz]'
LABEL_03_tanDelta = 'tan delta'
LABEL_04_capacitance = 'Kapazität Messsensor [F]'
LABEL_05_Vpeak = 'Û [V]'
LABEL_06_Vrms = 'Û/Wurzel(2) [V]'
LABEL_07_current = 'Strom [A]'
LABEL_08_notes = 'Hinweis'

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
        LABEL_02_frequency: _sourcerow[LABEL_02_frequency],
        LABEL_03_tanDelta:_sourcerow[LABEL_03_tanDelta],
        LABEL_04_capacitance: _sourcerow[LABEL_04_capacitance],
        LABEL_05_Vpeak: _sourcerow[LABEL_05_Vpeak],
        LABEL_06_Vrms: _meanVrms,
        LABEL_07_current: _sourcerow[LABEL_07_current],
        LABEL_08_notes: sourcerow[LABEL_08_notes]
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
        # take timestamp and other values (apart from tand) from first measurement of current frequqncy range
        _sourcerow = _current_vals[0]
        _meanTanD = my_mean(_current_vals, LABEL_03_tanDelta)
        _new_row = {
            LABEL_01_time: _sourcerow[LABEL_01_time],
            LABEL_02_frequency: _sourcerow[LABEL_02_frequency],
            LABEL_03_tanDelta: _meanTanD,
            LABEL_04_capacitance: _sourcerow[LABEL_04_capacitance],
            LABEL_05_Vpeak: _sourcerow[LABEL_05_Vpeak],
            LABEL_06_Vrms: _sourcerow[LABEL_06_Vrms],
            LABEL_07_current: _sourcerow[LABEL_07_current],
            LABEL_08_notes: _sourcerow[LABEL_08_notes]
        }

        #slices[sliceIndex].append(pd.DataFrame.from_records([_new_row]))
        slices[sliceIndex].append(_new_row)

        print("  [+] added mean of tanD={} for frequency {}".format(_meanTanD, _curr_freq))

    # ingest CSV
    allDataAsDict = pd.read_csv(fileName,
                                header=None,
                                skiprows=1,
                                sep=";",    # yep, it's different with that given CSV file!! (e.g. "to04_LCDI_0203.csv")
                                names=[LABEL_01_time,
                                       LABEL_02_frequency,
                                       LABEL_03_tanDelta,
                                       LABEL_04_capacitance,
                                       LABEL_05_Vpeak,
                                       LABEL_06_Vrms,
                                       LABEL_07_current,
                                       LABEL_08_notes]
                                )
    _current_vals = []
    _curr_freq = None
    for _num, _row in allDataAsDict.iterrows():
        _freq = float(_row[LABEL_02_frequency])
        ## abort on non-number inputs
        if np.isnan(_freq):
            continue

        _freq = round(_freq)

        _slice_len = slices[sliceIndex].__len__()
        if _slice_len > 0:
            currentMean = my_mean(slices[sliceIndex], LABEL_06_Vrms)
            currentValue = _row[LABEL_06_Vrms]

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

# create our list. CSV1
lists1 = split_CSV_to_DataFrames(mycsvdatei1)

print("\nResult\n-----")
print("We found {0} lists".format(lists1.__len__()))
idx = 0
for _sublist1 in lists1:
    print("  --> list {0} has {1} entries".format(idx, _sublist1.__len__()))
    idx += 1

    # we need to convert to dataframe first...
    _frame = pd.DataFrame.from_records(_sublist1)
    currentMean = my_mean(_sublist1, LABEL_06_Vrms)
    currentMean_rounded = int(currentMean / 100) * 100
    print("  --> mean Vrms is {}".format(currentMean))
    print("  --> rounded Vrms is {}".format(currentMean_rounded))

    # now we have our timeseries for current iteration.
    frequencies1 = _frame[LABEL_02_frequency]
    tanDeltas1 = _frame[LABEL_03_tanDelta]

    # provide our values to plot lib
    plt.plot(frequencies1, tanDeltas1, color=color1, label = label1, marker='o', linewidth=1)

# =============================================================================
# # create our list. CSV2
# lists2 = split_CSV_to_DataFrames(mycsvdatei2)
#
# print("\nResult\n-----")
# print("We found {0} lists".format(lists2.__len__()))
# idx = 0
# for _sublist2 in lists2:
#     print("  --> list {0} has {1} entries".format(idx, _sublist2.__len__()))
#     idx += 1
#
#     # we need to convert to dataframe first...
#     _frame = pd.DataFrame.from_records(_sublist2)
#     currentMean = my_mean(_sublist2, LABEL_03_Vrms)
#     currentMean_rounded = int(currentMean / 100) * 100
#     print("  --> mean Vrms is {}".format(currentMean))
#     print("  --> rounded Vrms is {}".format(currentMean_rounded))
#
#     # now we have our timeseries for current iteration.
#     frequencies2 = _frame[LABEL_05_frequency]
#     tanDeltas2 = _frame[LABEL_02_tanDelta]
#
#     # provide our values to plot lib
#     plt.plot(frequencies2, tanDeltas2, color=color2, label = label2, marker='o', linewidth=1)
#
# # create our list. CSV3
# lists3 = split_CSV_to_DataFrames(mycsvdatei3)
#
# print("\nResult\n-----")
# print("We found {0} lists".format(lists3.__len__()))
# idx = 0
# for _sublist3 in lists3:
#     print("  --> list {0} has {1} entries".format(idx, _sublist3.__len__()))
#     idx += 1
#
#     # we need to convert to dataframe first...
#     _frame = pd.DataFrame.from_records(_sublist3)
#     currentMean = my_mean(_sublist3, LABEL_03_Vrms)
#     currentMean_rounded = int(currentMean / 100) * 100
#     print("  --> mean Vrms is {}".format(currentMean))
#     print("  --> rounded Vrms is {}".format(currentMean_rounded))
#
#     # now we have our timeseries for current iteration.
#     frequencies3 = _frame[LABEL_05_frequency]
#     tanDeltas3 = _frame[LABEL_02_tanDelta]
#
#     # provide our values to plot lib
#     plt.plot(frequencies3, tanDeltas3, color=color3, label = label3, marker='o', linewidth=1)
#
# # create our list.CSV4
# lists4 = split_CSV_to_DataFrames(mycsvdatei4)
#
# print("\nResult\n-----")
# print("We found {0} lists".format(lists4.__len__()))
# idx = 0
# for _sublist4 in lists4:
#     print("  --> list {0} has {1} entries".format(idx, _sublist4.__len__()))
#     idx += 1
#
#     # we need to convert to dataframe first...
#     _frame = pd.DataFrame.from_records(_sublist4)
#     currentMean = my_mean(_sublist4, LABEL_03_Vrms)
#     currentMean_rounded = int(currentMean / 100) * 100
#     print("  --> mean Vrms is {}".format(currentMean))
#     print("  --> rounded Vrms is {}".format(currentMean_rounded))
#
#     # now we have our timeseries for current iteration.
#     frequencies4 = _frame[LABEL_05_frequency]
#     tanDeltas4 = _frame[LABEL_02_tanDelta]
#
#     # provide our values to plot lib
#     plt.plot(frequencies4, tanDeltas4, color=color4, label = label4, marker='o', linewidth=1)
# =============================================================================

plt.xlabel("Frequenz (Hz)", fontsize=40)
plt.ylabel("tan d", fontsize=40)
plt.xlabel(r'$f$ / Hz $\rightarrow$', fontsize=40)
plt.ylabel(r'tan $\delta$ $\rightarrow$', fontsize=40)
plt.xticks(np.arange(0, 2100, step=500), fontsize=30)
plt.yticks(np.arange(0, 30e-3, step=5e-3), fontsize=30)
ax.grid(which='both', linestyle='--', linewidth=1)
plt.legend(fontsize=30)