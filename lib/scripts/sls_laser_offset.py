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

sls.write_line('get OffsetFrequency')
time.sleep(.1)
a = sls.read()
a= a.split('\n')
a= a[1][16:].split('E')

a= float(a[0])*10**(float(a[1][1:3]))
print(a)

n=500
f_step = -10e3
f_start = a
f_stop = a + f_step*n # Hz
step_delay = 0.003 #(seconds)


#n_steps = (f_stop-f_start)/f_step + 1
#for f_idx in range(f_start, f_stop, f_step)
for idx in range(0, n):
    f_idx = f_start + f_step*idx
    sls.write_line('set OffsetFrequency ' + str(f_idx))
    time.sleep(step_delay)
    


    
##sls.write_line('get values')
###val =sls.read()
###print(val)
##time.sleep(.1)
##val =sls.read()
#print(val)


##sls.flushinput()  
##sls.flushoutput()    
##sls.write_line('get OffsetFrequency')
##time.sleep(.1)
##a = sls.read()
##print(a)


sls.close()

 
