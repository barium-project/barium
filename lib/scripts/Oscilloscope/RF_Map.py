


import labrad
import numpy as np
import time
from datetime import datetime
from keysight import command_expert as kt
from labrad.units import WithUnit as U
from scipy.optimize import curvefit

# Connect to labrad
cxn_bender = labrad.connect('bender')
print 'Connected to Labrad'

# Connect to devices


trap = cxn_bender.trap_server

file_loc = 'rf_settings'



start_voltage = 50
stop_voltage = 300
voltage_step = 5
max_voltage_itt = 25
voltage_convergence = .01
voltage_guess = 0


start_phase = 11
phast_step = .5
max_phase_itt = 25
phase_convergence = .05

total_v_points = ((start_voltage-stop_voltage)/voltage_step) + 1


rf_map = np.zeros((total_v_points,3))
rf_map[:,0] = np.linspace(start_voltage,stop_voltage,total_voltage_points)

for i in range(total_voltage_points):
    # initialize settings for next voltage set point
    trap.set_amplitude(rf_map[i,0],2)
    trap.update_rf()
    step_passed = 0
    phase_guess = 0
    for j in range(max_voltage_itt):
        # start chan3 iteration
        if step_passed == 0:
            trap.set_amplitude(rf_map[i,0] + voltage_guess,3)
            trap.update_rf()
            [time_step, ch1, ch2, ch3, ch4] = kt.run_sequence('read_voltages')
            time_array = np.linspace(1,np.len(ch3),np.len(ch3))*time_step

            plot(time_array,ch3)
            plot(time_array,ch4)
            show()

            fit2 = curve_fit(sin_wave,time_array,ch3)
            fit3 = curve_fit(sin_wave,time_array,ch4)

            amplitude2 = fit2[0][0]
            phase2 = fit2[0][1]
            amplitude3 = fit3[0][0]
            phase3 = fit3[0][1]

            # if did not converge then adjust voltages
            if (amplitude3-amplitude2)/amplitude2 > voltage_convergence:
                if amplitude3-amplitude2 > 0:
                    voltage_guess = voltage_guess - 1.0
                else:
                    voltage_guess = voltage_guess + 1.0
                print voltage_guess
                if j == max_voltage_itt -1:
                    print "voltage point " + str(rf_map[i,0]) + 'V failed'
            else:
                # if they did converge check the phase difference
                if (phase3 - phase2)/phase2 > phase_convergence:
                    if phase3-phase2 > 0:
                        phase_guess = phase_guess - 1
                        trap.set_phase(start_phase + phase_guess,3)
                        trap.update_rf()
                    else:
                        phase_guess = phase_guess + 1
                        trap.set_phase(start_phase + phase_guess,3)
                        trap.update_rf()
                    print phase_guess
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


def sin_wave(x, A, phi):
    return A*np.sin(2*np.pi*1.099e6*x + phi)

