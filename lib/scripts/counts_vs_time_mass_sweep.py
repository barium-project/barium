# Script to take counts vs time
# Justin Christensen 2/18/16


import labrad
import numpy as np
import time
from datetime import datetime
from labrad.units import WithUnit as U

# Connect to labrad
cxn = labrad.connect(name = 'mass spec experiment')
print 'Connected to Labrad'

# Connect to devices
rga = cxn.planet_express_serial_server_cg
sca = cxn.sr430_scalar_server
hp = cxn.hp6033a_server


# Set the baudrate and address for the RGA
rga.open()
rga.baudrate(28800)

# Set the GPIB address

sca.select_device()
hp.select_device()

# Set SCALAR parameters

DISCRIMINATOR_LEVEL = U(0.2,'V')  ### Edit this to change the discriminator level
sca.discriminator_level(DISCRIMINATOR_LEVEL)# set discriminator level
RECORDS_PER_SCAN = 1000              ### Edit this to change the records per scan
sca.records_per_scan(RECORDS_PER_SCAN) # set records per scan
sca.bins_per_record(1024)              # set bins per record
sca.bin_width(163840)                  # set bin width

# Set RGA mass to look at
MASS_LIST = [133,138]         ### Edit this to change this list of masses to sweep through
rga.write_line('hv2200')
rga.write_line('fl1')
time.sleep(1)

# Set the POWER SUPPLY Parameters
FILAMENT_CURRENT = U(13.5,'A')      ### Edit this to change the power supply current
hp.set_voltage(U(20,'V'))
hp.set_current(FILAMENT_CURRENT)

# Provide the TRIGGER parameters
TRIGGER_FREQUENCY = 5.8             ### Edit this to provide the trigger frequency (in Hz)
trigger_period = 1/TRIGGER_FREQUENCY
counting_time = RECORDS_PER_SCAN*trigger_period + 1 #in seconds

# time in seconds between each data point
exp_t = 1

SWEEP_ITERATIONS = 1               ### Edit this to change the number of sweeps
CURRENT_LIST = [10+0.25*i for i in range(15)]  ##initial current + current increment*index (10 to 13.5)

#Initialize data array(mass,counts,day,hour,minute,second,voltage,current)
results = np.array([[0,0,0,0,0,0,0,0]])

# Acquire the data
for iteration in range(SWEEP_ITERATIONS):
    for iterative_current in CURRENT_LIST:
        hp.set_current(U(iterative_current,'A'))
        for mass in MASS_LIST:
            if mass > 100:
                sca.discriminator_level(U(0.22,'V'))
                print '220mV Discrim'
            else:
                sca.discriminator_level(DISCRIMINATOR_LEVEL)
                print '200mV Discrim'
            rga.write_line('ml'+str(mass)) # selects the mass
            sca.clear_scan() # clear the last run
            sca.start_new_scan(U(counting_time,'s')) # start scan
            counts = float(sca.get_counts()) # Do the statistics
            time.sleep(3) # Give time to calculate
            t = datetime.now().timetuple()
            voltage = hp.get_voltage()['V']
            current = hp.get_current()['A']
            new_data = np.array([[mass,counts,t[2],t[3],t[4],t[5],voltage,current]])
            print iteration, new_data
            results = np.concatenate((results,new_data),axis = 0)
            np.savetxt('Z:/Group_Share/Barium/Data/2016/6/24/Barium_Spec_vs_current_longrun.txt',results,fmt="%0.5e")
            time.sleep(exp_t) # Wait to do next run
    
# close ports

hp.set_current(U(0,'A'))
rga.write_line('hv0')
rga.write_line('fl0')
rga.close()