# Script to take counts vs time
# Justin Christensen 2/18/16


import labrad
import numpy as np
import time
from datetime import datetime
from labrad.units import WithUnit as U

# Connect to labrad
cxn = labrad.connect('bender',password='lab')
print 'Connected to Labrad'

# Connect to devices

sr = cxn.sr430_scalar_server
sr.select_device()

# Total time in seconds to run exp
total_t = 60*60*13

# time to get counts in seconds
counts_time = 45

# time in seconds between each data point
exp_t = 15*60

total_runs = total_t/(exp_t+counts_time)

#Initialize data array(mass,counts,day,hour,minute,second)
results = np.array([[0,0,0,0,0,0]])
mass = 39
# Acquire the data
for i in range(total_runs):
    sr.start_new_scan(U(counts_time,'s'))
    counts = sr.get_counts()
    t = datetime.now().timetuple()
    new_data = np.array([[mass,counts,t[2],t[3],t[4],t[5]]])
    print new_data
    results = np.concatenate((results,new_data),axis = 0)
    np.savetxt('Z:/Group_Share/Barium/Data/2016/12/20/mass39_counts_vs_time_pt_tube.txt',results,fmt="%0.5e")
    time.sleep(exp_t) # Wait to do next run
    
