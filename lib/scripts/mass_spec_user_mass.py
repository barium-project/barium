### Script to take a mass spectrum on the SRS RGA200
### This is written to work on a specific computer since the labrad
### servers incorporate the computer name.

# Parameter List, Only changes these values. Double click to run.
##############################################################################
rga_port = "COM1"
labrad_manager_address = 'localhost' # if running on a different comp use that ip address
discriminator_level = .06 # In volts
records_per_scan = 160
# mass_min = 85 #amu
# mass_max = 89 #amu
# number_of_points = 17
# Time required for sr430 to count at each point. Must confirm this before you run.
masses = [86.5, 88.3]
count_time = 30
file_location = 'Z:/Group_Share/Barium/Data/2016/5/17'
# Must enter the bias voltage on the filament
bias_v = 6.6 # V
# Power Supply Settings (Amps)
ps_voltage = 25.0  #Volts (Max Voltage)
ps_current = 14.0  #Amps (Actual Current)
##############################################################################

import labrad
import numpy as np
import time
from datetime import datetime
from labrad.units import WithUnit as U


cxn = labrad.connect(labrad_manager_address)
print 'Connected to Labrad'

# Connect to servers
rga = cxn.planet_express_serial_server
sr430 = cxn.sr430_scalar_server
hp = cxn.hp6033a_server 


# Set the baudrate and address for the RGA
rga.open(rga_port)
rga.baudrate(28800)


# Set the GPIB address

sr430.select_device()
hp.select_device()


# Set scalar parameters

sr430.discriminator_level(U(discriminator_level,'V'))
sr430.records_per_scan(records_per_scan)



#Initialize results array(mass,counts,day,hour,minute,second,voltage,current)
results = np.array([[0,0,0,0,0,0,0,0]])

#Set the power supply settings and wait for conditions to steady
hp.set_voltage(U(ps_voltage,'V'))
hp.set_current(U(ps_current,'A'))
time.sleep(3)

for i in range(len(masses)):

    rga.write_line('ml'+str(masses[i]))
    time.sleep(1)

    # Acquire the data

    sr430.start_new_scan(U(count_time,'s'))
    counts = sr430.get_counts()
    t = datetime.now().timetuple() # get the time
    voltage = hp.get_voltage()['V'] # get power supply voltage and current
    current = hp.get_current()['A']
    new_data = np.array([[masses[i],counts,t[2],t[3],t[4],t[5],voltage,current]])
    print new_data
    results = np.concatenate((results,new_data),axis = 0)
    file_name = file_location+'/mass_spec_'+str(masses[0])+'amu_'+str(masses[len(masses)-1])+'amu_'+str(bias_v)+'Vbias_'+str(count_time)+'s.txt'
    np.savetxt(file_name,results,fmt="%0.5e")


# close ports
rga.close()

# Set the current to zero
c = U(0,'A')
# hp.set_current(c)
