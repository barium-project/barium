


import labrad
import numpy as np
import time
from datetime import datetime
from keysight import command_expert as kt
from labrad.units import WithUnit as U

# Connect to labrad
cxn_planet_express = labrad.connect('planetexpress', password = 'lab')
cxn_bender = labrad.connect('bender', password = 'lab')
print 'Connected to Labrad'

# Connect to devices

hp = cxn_planet_express.hp6033a_server
hp.select_device()

trap = cxn_bender.trap_server


total_runs = 40
load_time = 0 # Time the filament is on
reaction_time =  15 # Time in between loading and pulsing
current1 = U(5,'A')
current2 = U(6.75,'A')
current3 = U(0,'A')
voltage1 = U(1.5,'V')
a_ramp_v = 0
HV1 = 900
HV2 = 845
HV3 = 1400
HV4 = 1400



#trap.set_hv(HV1,3)
#trap.set_hv(HV2,1)
#trap.set_hv(HV3,2)
#trap.set_hv(HV4,0)





#hp.set_voltage(voltage1)
# Acquire the data
for i in range(total_runs):
    channel1  = np.zeros((1,10000))
    channel2  = np.zeros((1,10000))
    channel3  = np.zeros((1,10000))
    channel4  = np.zeros((1,10000))

    #trap.set_dc(a_ramp_v,2)
    #trap.set_dc(a_ramp_v,3)
    #hp.set_current(current1)
    #hp.set_current(current2)
    #time.sleep(load_time)
    #hp.set_current(current3)
    #time.sleep(5)
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
    channel1[0,:] = ch1
    channel2[0,:] = ch2
    channel3[0,:] = ch3
    channel4[0,:] = ch4


    file_loc = 'Z:/Group_Share/Barium/Data/2016/11/7/TOF_Data/run0'
    data_string = '#[number of traces,time step in voltage data, loading time, load current, reaction time, rod1V, rod2V, rod3V, rod4V, rod1 DCV, rod3 DCV, ablation]'
    data = np.array([total_runs,time_step,load_time,current2['A'],reaction_time,HV1,HV2,HV3,HV4,a_ramp_v,a_ramp_v])
    np.savetxt(file_loc+'/' + str(i+1) + '_parameters.txt',data,fmt="%0.5e",
           header = data_string, comments = '')
    np.savetxt(file_loc+'/' + str(i+1) + '_hv_3.txt',channel1,fmt="%0.5f")
    np.savetxt(file_loc+'/'+ str(i+1) + '_hv_2.txt',channel2,fmt="%0.5f")
    np.savetxt(file_loc+'/' + str(i+1) + '_ttl_v.txt',channel3,fmt="%0.5f")
    np.savetxt(file_loc+'/'+ str(i+1) +'_tof_v.txt',channel4,fmt="%0.5f")

