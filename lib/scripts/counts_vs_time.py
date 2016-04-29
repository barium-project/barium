# Script to take counts vs time
# Justin Christensen 2/18/16


import labrad
import numpy as np
import time
from datetime import datetime

# Connect to labrad
cxn = labrad.connect(name = 'mass spec experiment')
print 'Connected to Labrad'

# Connect to devices
rga = cxn.planet_express_serial_server
sca = cxn.planet_express_gpib_bus
hp = cxn.hp6033a_server


# Set the baudrate and address for the RGA
rga.open()
rga.baudrate(28800)

# Set the GPIB address

sca.address('GPIB0::1::INSTR')
hp.select_device()

# Set scalar parameters

sca.write('dclv175e-3')# set discriminator level
sca.write('rscn1000') # set records per scan

# Set RGA mass to look at
mass = 138.25
rga.write_line('ml'+str(mass))
time.sleep(1)

# Total time in seconds to run exp
total_t = 60*60*24*3

# time to get counts in seconds
counts_time = 215

# time in seconds between each data point
exp_t = 2*60

total_runs = total_t/(exp_t+counts_time)

#Initialize data array(mass,counts,day,hour,minute,second,voltage,current)
results = np.array([[0,0,0,0,0,0,0,0]])

# Acquire the data
for i in range(total_runs):
    sca.write('clrs') # clear the last run
    sca.write('sscn') # start scan
    time.sleep(counts_time) # wait for scan to finish 
    sca.write('stat') # Do the statistics
    print "do  stats"
    time.sleep(3) # Give time to calculate
    sca.write('spar?2') # get total counts
    print "get stats"
    counts = float(sca.read(256))# read the counts
    t = datetime.now().timetuple()
    voltage = hp.get_voltage()['V']
    current = hp.get_current()['A']
    new_data = np.array([[mass,counts,t[2],t[3],t[4],t[5],voltage,current]])
    print new_data
    results = np.concatenate((results,new_data),axis = 0)
    np.savetxt('Z:/Group_Share/Barium/Data/2016/3/4/mass138_counts_vs_time_7Vbias_167s.txt',results,fmt="%0.5e")
    time.sleep(exp_t) # Wait to do next run
    
# close ports

rga.close()
