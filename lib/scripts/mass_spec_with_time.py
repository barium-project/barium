### Script to take a mass spectrum
### As well as check mass 138 every 3rd point

import labrad
import numpy as np
import time
from datetime import datetime

cxn = labrad.connect(name = 'mass spec experiment')
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

sca.write('dclv175e-3')# set discriminator level
sca.write('rscn200') # set records per scan


# Select the mass range

m_max = 140
m_min = 131
n_points = 19

# Set how long to wait to count in sec

count_time = 30*60

#Initialize results array(mass,counts,day,hour,minute,second,voltage,current)
mass_results = np.array([[0,0,0,0,0,0,0,0]])
time_results = np.array([[0,0,0,0,0,0,0,0]])

mass = np.linspace(m_min,m_max,n_points)

for i in range(n_points):

    
    if mass[i] % 4 == 0:
        rga.write_line('ml145')
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
        new_data = np.array([[137,counts,t[2],t[3],t[4],t[5],voltage,current]])
        print new_data
        time_results = np.concatenate((time_results,new_data),axis = 0)
        np.savetxt('Z:/Group_Share/Barium/Data/2016/2/26/control_137_vs_t33s_12vbias.txt',time_results,fmt="%0.5e")
        
    
    rga.write_line('ml'+str(mass[i]))
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
    new_data = np.array([[mass[i],counts,t[2],t[3],t[4],t[5],voltage,current]])
    print new_data
    mass_results = np.concatenate((mass_results,new_data),axis = 0)
    np.savetxt('Z:/Group_Share/Barium/Data/2016/2/26/control_mass_spec_64_140_12Vbias_33s.txt',mass_results,fmt="%0.5e")
        

# close ports
rga.close()




