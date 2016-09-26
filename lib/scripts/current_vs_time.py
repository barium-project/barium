# Script to take counts vs time
# Justin Christensen 2/18/16


import labrad
import numpy as np
import time
from datetime import datetime
from labrad.units import WithUnit as U

# Connect to labrad
cxn = labrad.connect(name = ' loading experiment')
print 'Connected to Labrad'

# Connect to devices
hp = cxn.hp6033a_server


# Set the GPIB address

hp.select_device()

voltage = 1.5
current = 6.25
wait_time = 60


v = U(voltage,'V')
c  = U(current,'A')

hp.set_voltage(v)
hp.set_current(c)
time.sleep(wait_time)

current = 0.02
c  = U(current,'A')
hp.set_current(c)

