import labrad
import serial
import os
import time


LABRADNODE = os.environ['LABRADNODE']
cxn = labrad.connect()
sls = cxn.bender_serial_server
print(sls.list_serial_ports())
print(sls.open('COM13'))
sls.baudrate(115200)

freq = '80e6'
sls.write_line('set OffsetFrequency ' + freq)

sls.write_line('get OffsetFrequency')
time.sleep(.1)
val =sls.read()
print(val)


sls.close()

 
