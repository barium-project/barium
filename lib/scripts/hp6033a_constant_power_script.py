import labrad
from labrad.units import WithUnit as U
cxn = labrad.connect()

hp = cxn.hp6033a_server
hp.select_device(0)
hp.set_voltage(U(20,'V'))

DESIRED_POWER = 10. #Watts
refvoltage = 1. #Volts

current = U(DESIRED_POWER/refvoltage,'A')

tolerable_error = False
i=0
while tolerable_error == False:
    hp.set_current(current)
    voltage = hp.get_voltage
    if 1 - (current['A']*voltage['V']/DESIRED_POWER) < 1/60:
        tolerable_error == True
    print i, voltage, current
    current = DESIRED_POWER/voltage
    i+=1
    
