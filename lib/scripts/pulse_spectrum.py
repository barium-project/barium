# Script to take a pulse height spectrum of the
# SRS430 multi-channel scalar
# Justin Christensen 1/13/16


import labrad
import numpy as np
import time
from datetime import datetime

# Connect to labrad
cxn = labrad.connect()

print "Connected to labrad\n"

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

sca.write('rscn200') # set records per scan


# Set RGA mass to look at
mass = 138
rga.write_line('ml'+str(mass))
time.sleep(1)

# Number of points
n_points = 41
minV = .1
maxV = .3
counts_time = 46 # wait time in seconds to let sca count

# Define arrays
discV = np.linspace(minV,maxV,n_points)
counts = np.zeros(n_points)

#Initialize data array(disc,counts,day,hour,minute,second,voltage,current)
results = np.array([[0,0,0,0,0,0,0,0]])

# Acquire the data
for i in range(n_points):
    sca.write('dclv'+str(discV[i]))
    sca.write('clrs') # clear the last run
    sca.write('sscn') # start scan
    time.sleep(counts_time) # wait for scan to finish 
    sca.write('stat') # Do the statistics
    print "do stats"
    time.sleep(3) # Give time to calculate
    sca.write('spar?2') # get total counts
    print "get stats"
    counts = float(sca.read(256))# read the counts
    t = datetime.now().timetuple()
    voltage = hp.get_voltage()['V']
    current = hp.get_current()['A']
    new_data = np.array([[discV[i],counts,t[2],t[3],t[4],t[5],voltage,current]])
    print new_data
    results = np.concatenate((results,new_data),axis = 0)    
    
    np.savetxt('Z:/Group_Share/Barium/Data/2016/2/24/mass_138_pulse_spect_33s.txt',results,fmt="%0.5e")
    
# close ports

