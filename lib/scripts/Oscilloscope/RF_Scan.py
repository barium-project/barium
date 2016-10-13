


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
cam = cxn_bender.andor_server


start_voltage = 100
stop_voltage = 400
return_voltage = 150
voltage_step = 10
warm_up_time = 30 #sec

current1 = U(5,'A')
current2 = U(6.5,'A')
current3 = U(0,'A')
voltage1 = U(1.5,'V')

HV1 = 900
HV2 = 855
HV3 = 1400
HV4 = 1400

rod1_dc = 0 #V
rod3_dc = 0


total_v_points = ((stop_voltage-start_voltage)/voltage_step) + 1
voltages = np.linspace(start_voltage,stop_voltage,total_v_points)

rf_map = np.loadtxt('C:/Users/barium133/Code/barium/lib/clients/TrapControl_client/rf_map.txt')


index = np.where(rf_map[:,0] == start_voltage)
index = index[0][0]
trap.set_amplitude(rf_map[index,0],2)
trap.set_amplitude(rf_map[index,1],3)
trap.set_phase(rf_map[index,2],3)
trap.update_rf()


hp.set_voltage(voltage1)
hp.set_current(current1)
hp.set_current(current2)
time.sleep(warm_up_time)
print "Ramp Starting"
# step through voltages
for i in range(total_v_points):
    index = np.where(rf_map[:,0] == voltages[i])
    index = index[0][0]
    trap.set_amplitude(rf_map[index,0],2)
    trap.set_amplitude(rf_map[index,1],3)
    trap.set_phase(rf_map[index,2],3)
    trap.update_rf()
    time.sleep(.1)
    print voltages[i]

time.sleep(1)
index = np.where(rf_map[:,0] == return_voltage)
index = index[0][0]
trap.set_amplitude(rf_map[index,0],2)
trap.set_amplitude(rf_map[index,1],3)
trap.set_phase(rf_map[index,2],3)
trap.update_rf()

hp.set_current(current3)
time.sleep(5)

trap.set_dc_rod(rod1_dc,3)
trap.set_dc_rod(rod3_dc,2)
time.sleep(3)
trap.set_dc_rod(0,3)
trap.set_dc_rod(0,2)
time.sleep(2)

'''
identify_exposure = U(0.2, 's')
start_x = 1; stop_x = 512
start_y = 1; stop_y = 512
image_region = (2,2,start_x,stop_x,start_y,stop_y)

pixels_x = (stop_x - start_x + 1)/2
pixels_y = (stop_y - start_y + 1)/2


cam.abort_acquisition()
initial_exposure = cam.get_exposure_time()
cam.set_exposure_time(identify_exposure)
initial_region = cam.get_image_region()
cam.set_image_region(*image_region)
cam.set_acquisition_mode('Single Scan')
cam.set_shutter_mode('Auto')
cam.start_acquisition()
cam.wait_for_acquisition()
image = cam.get_most_recent_image(None)
cam.abort_acquisition()
cam.set_shutter_mode('Close')




cam.set_exposure_time(initial_exposure)
cam.set_image_region(initial_region)
cam.start_live_display()
image = np.reshape(image, (pixels_y, pixels_x))


file_loc = 'Z:/Group_Share/Barium/Data/2016/10/4/RF_Scan/run14/'
np.savetxt(file_loc + 'rf_scan_' + str(voltage_step) + 'V.txt', image)
counts = np.sum(np.sum(image))
print counts
np.savetxt(file_loc + 'total_counts_' + str(voltage_step) + 'V.txt', [counts], fmt="%0.5e")


channel1  = np.zeros((1,10000))
channel2  = np.zeros((1,10000))
channel3  = np.zeros((1,10000))
channel4  = np.zeros((1,10000))

trap.trigger_hv_pulse()
# The below command will grab the scope traces. Scope needs to be in single mode
[time_step, ch1, ch2, ch3, ch4] = kt.run_sequence('read_voltages')
channel1[0,:] = ch1
channel2[0,:] = ch2
channel3[0,:] = ch3
channel4[0,:] = ch4



data_string = '#[start_voltage, stop voltage, voltage step, load current, warm_up_time, rod1V, rod2V, rod3V, rod4V, rod1 DCV, rod3 DCV, pt]'
data = np.array([start_voltage,stop_voltage,voltage_step,current2['A'],warm_up_time,HV1,HV2,HV3,HV4,rod1_dc,rod3_dc])
np.savetxt(file_loc+ '/parameters.txt',data,fmt="%0.5e",
           header = data_string, comments = '')
np.savetxt(file_loc+'/hv_3.txt',channel1,fmt="%0.5f")
np.savetxt(file_loc+'/hv_2.txt',channel2,fmt="%0.5f")
np.savetxt(file_loc+'/ttl_v.txt',channel3,fmt="%0.5f")
np.savetxt(file_loc+'/tof_v.txt',channel4,fmt="%0.5f")
'''

