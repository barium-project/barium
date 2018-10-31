# Script to take counts vs time
# Justin Christensen 2/18/16


import labrad
import numpy as np
import time
from datetime import datetime

# Connect to labrad
cxn = labrad.connect(name = 'get counts')
print 'Connected to Labrad'

total_runs = 300
# Connect to devices
p = cxn.pulser

pmt_counts = np.array([])
# Acquire the data
for i in range(total_runs):
    time.sleep(.5)
    counts = p.get_pmt_counts()
    if len(counts) != 0:
        pmt_counts = np.append(pmt_counts, counts[0][0])

print np.mean(pmt_counts), len(pmt_counts)

