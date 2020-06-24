


import labrad
import numpy as np
import time
from datetime import datetime
from keysight import command_expert as kt
from labrad.units import WithUnit as U
from scipy.optimize import curve_fit
from pylab import *

# Connect to labrad
cxn_bender = labrad.connect('bender', password = 'lab')
print 'Connected to Labrad'

# Connect to devices


trap = cxn_bender.trapserver

file_loc = 'rf_settings_101_400.txt'



start_voltage = 101
stop_voltage = 400
voltage_step = 1
max_voltage_itt = 100
voltage_convergence = .003
voltage_guess = 0


start_phase = 41.2
phase_step = .5
max_phase_itt = 25
phase_convergence = .005

total_v_points = ((stop_voltage-start_voltage)/voltage_step) + 1
print total_v_points

rf_map = np.zeros((total_v_points,3))
rf_map[:,0] = np.linspace(start_voltage,stop_voltage,total_v_points)

def sin_wave(x, A, phi, C):
    return A*np.sin(2*np.pi*1.099e6*x + phi) + C



for i in range(int(total_v_points)):
    # initialize settings for next voltage set point
    trap.set_amplitude(rf_map[i,0],2)
    trap.update_rf()
    step_passed = 0
    phase_guess = 0
    for j in range(max_voltage_itt):
        # start chan3 iteration
        print 'Step: ' + str(j)
        if step_passed == 0:
            trap.set_amplitude(rf_map[i,0] + voltage_guess,3)
            trap.update_rf()
            [time_step, ch1, ch2, ch3, ch4] = kt.run_sequence('rf_map')
            time_array = np.linspace(1,len(ch3),len(ch3))*time_step

            fit2 = curve_fit(sin_wave,time_array,ch2)
            fit3 = curve_fit(sin_wave,time_array,ch1)

            amplitude2 = fit2[0][0]
            phase2 = fit2[0][1]
            offset2 = fit2[0][2]
            amplitude3 = fit3[0][0]
            phase3 = fit3[0][1]
            offset3 = fit3[0][2]

            #dat = sin_wave(time_array,amplitude2,phase2,offset2)

            #Use to check fit
            #plot(time_array,ch2)
            #plot(time_array,dat)
            #show()

            print amplitude2, phase2, offset2
            print amplitude3, phase3, offset3

            # if did not converge then adjust voltages
            if abs(amplitude3-amplitude2)/abs(amplitude2) > voltage_convergence:
                if amplitude3-amplitude2 > 0:
                    voltage_guess = voltage_guess - voltage_step
                else:
                    voltage_guess = voltage_guess + voltage_step
                print voltage_guess
                if j == max_voltage_itt -1:
                    # If failed save current point
                    print "voltage point " + str(rf_map[i,0]) + 'V failed'
                    rf_map[i,1] = rf_map[i,0]+voltage_guess
                    rf_map[i,2] = start_phase + phase_guess
                    start_phase = start_phase + phase_guess
            else:
                # if they did converge check the phase difference
                if abs(phase3 - phase2) > phase_convergence:
                    if phase3-phase2 > 0:
                        phase_guess = phase_guess - phase_step
                        trap.set_phase(start_phase + phase_guess,3)
                        trap.update_rf()
                    else:
                        phase_guess = phase_guess + phase_step
                        trap.set_phase(start_phase + phase_guess,3)
                        trap.update_rf()
                    print phase_guess
                    if j == max_voltage_itt -1:
                        # If failed save current point
                        print "voltage point " + str(rf_map[i,0]) + 'V failed'
                        rf_map[i,1] = rf_map[i,0]+voltage_guess
                        rf_map[i,2] = start_phase + phase_guess
                        start_phase = start_phase + phase_guess

                else:
                    # everything converged. save point
                    rf_map[i,1] = rf_map[i,0]+voltage_guess
                    rf_map[i,2] = start_phase + phase_guess
                    start_phase = start_phase + phase_guess
                    print "voltage point " + str(rf_map[i,0]) + 'V passed'
                    step_passed = 1
        else:
            break



data_string = '#[channel 2 V, channel 3 V, channel 3 phase]'
data = np.array(rf_map)
np.savetxt(file_loc, data , fmt="%0.5e", header = data_string, comments = '')


