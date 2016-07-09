import labrad
import os
LABRADNODE = os.environ['LABRADNODE']
cxn = labrad.connect()

command = 'gp = cxn.'+LABRADNODE.lower()+'_gpib_bus'
exec command

devices = gp.list_devices()
gp.address(devices[1])

for i in range(100):
    gp.write('DCLV?')
    print i,'DCLV?'
    message = gp.read()
    print i,message
    gp.write('DCLV?')
    gp.write('RSCN?')
    print i,'DCLV?'
    print i,'RSCN?'
    message = gp.read()
    print i,message
