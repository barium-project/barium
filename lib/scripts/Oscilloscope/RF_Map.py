


import labrad
import numpy as np
import time
from datetime import datetime
from keysight import command_expert as kt
from labrad.units import WithUnit as U

# Connect to labrad
cxn_bender = labrad.connect('bender')
print 'Connected to Labrad'

# Connect to devices


trap = cxn_bender.trap_server

file_loc = 'Z:/Group_Share/Barium/Data/2016/9/13/TOF_Data/run2'



channel1  = np.zeros((total_runs,10000))
channel2  = np.zeros((total_runs,10000))
channel3  = np.zeros((total_runs,10000))
channel4  = np.zeros((total_runs,10000))


#hp.set_voltage(voltage1)
# Acquire the data
for i in range(total_runs):
    #trap.set_dc(a_ramp_v,2)
    #trap.set_dc(a_ramp_v,3)
    #hp.set_current(current1)
    #time.sleep(3)
    #hp.set_current(current2)
    time.sleep(load_time)
    #hp.set_current(current3)
    #trap.set_dc(0,2)
    #trap.set_dc(0,3)
    #time.sleep(reaction_time)
    #raw_input("Press Enter")
    trap.trigger_loading()
    time.sleep(reaction_time)
    trap.trigger_hv_pulse()
    #time.sleep(1)
    # The below command will grab the scope traces. Scope needs to be in single mode
    [time_step, ch1, ch2, ch3, ch4] = kt.run_sequence('read_voltages')
    channel1[i,:] = ch1
    channel2[i,:] = ch2
    channel3[i,:] = ch3
    channel4[i,:] = ch4



data_string = '#[number of traces,time step in voltage data, loading time, load current, reaction time, rod1V, rod2V, rod3V, rod4V, rod1 DCV, rod3 DCV, albation]'
data = np.array([total_runs,time_step,load_time,current2['A'],reaction_time,HV1,HV2,HV3,HV4,a_ramp_v,a_ramp_v])
np.savetxt(file_loc+'/parameters.txt',data,fmt="%0.5e",
           header = data_string, comments = '')
np.savetxt(file_loc+'/hv_3.txt',channel1,fmt="%0.5f")
np.savetxt(file_loc+'/hv_2.txt',channel2,fmt="%0.5f")
np.savetxt(file_loc+'/ttl_v.txt',channel3,fmt="%0.5f")
np.savetxt(file_loc+'/tof_v.txt',channel4,fmt="%0.5f")


