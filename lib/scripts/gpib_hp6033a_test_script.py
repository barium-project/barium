import labrad
import os
LABRADNODE = os.environ['LABRADNODE']
cxn = labrad.connect()

command = 'gp = cxn.'+LABRADNODE.lower()+'_gpib_bus'
exec command

devices = gp.list_devices()
gp.address(devices[0])

for i in range(100):
    gp.write('VOLT:LEV:IMM?')
    gp.write('VOLT:LEV:IMM?')
    message = gp.read()
    print i,message
    gp.write('CURR:LEV:IMM?')
    message = gp.read()
    print i,message
