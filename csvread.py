import pandas as pd
import numpy as np
import os.path
import collections

csvarray = pd.read_csv("my.csv")

for line in csvarray:
    print(line)


