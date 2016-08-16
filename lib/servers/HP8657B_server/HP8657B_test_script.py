import labrad
from labrad.units import WithUnit as U
from time import sleep

cxn = labrad.connect('planetexpress',password='lab')

hp = cxn.hp8657b_server
devices = hp.list_devices()
hp.select_device(devices[0][1])

for i in range(10):
    hp.amplitude(U(-143.5+15*i,'dBm'))
    sleep(1)

for i in range(10):
    hp.amplitude_offset(U(-100+20*i,'dB'))
    sleep(1)

for i in range(10):
    hp.amplitude_modulation_step('up')
    sleep(1)

for i in range(20):
    hp.amplitude_modulation_step('down')
    sleep(1)

for i in range(10):
    hp.amplitude_modulation_increment(U(-100+20*i,'dB'))
    sleep(1)
