### Script to take a mass spectrum

import labrad
import numpy as np
import time
from datetime import datetime
from labrad.units import WithUnit as U

cxn = labrad.connect()
print 'Connected to Labrad'


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

sca.write('dclv300e-3')# set discriminator level
sca.write('rscn10000') # set records per scan


# Select the mass range

m_max = 140
m_min = 131
n_points = 100

# Set how long to wait to count in sec

count_time = 30*60

#Initialize results array(mass,counts,day,hour,minute,second,voltage,current)
results = np.array([[0,0,0,0,0,0,0,0]])

masses = [134,138,145]

#mass = np.linspace(m_min,m_max,n_points)

for i in range(n_points):

    for j in range(len(masses)):
        
        rga.write_line('ml'+str(masses[j]))
        time.sleep(1)

        # Acquire the data

        sca.write('clrs') # clear the last run
        sca.write('sscn') # start scan
        time.sleep(count_time) # wait for scan to finish
        sca.write('stat') # Do the statistics
        print "do stats"
        time.sleep(3) # Give time to calculate
        sca.write('spar?2') # get total counts
        counts = float(sca.read(256))# read the counts
        t = datetime.now().timetuple() # get the time
        voltage = hp.get_voltage()['V'] # get power supply voltage and current
        current = hp.get_current()['A']
        new_data = np.array([[masses[j],counts,t[2],t[3],t[4],t[5],voltage,current]])
        print new_data
        results = np.concatenate((results,new_data),axis = 0)
        np.savetxt('Z:/Group_Share/Barium/Data/2016/3/16/mass_spec_134_138_145_7Vbias_1640s_100ug.txt',results,fmt="%0.5e")


# close ports
rga.close()

# Set the current to zero
#c = U(0,'A')
#hp.set_current(c)

