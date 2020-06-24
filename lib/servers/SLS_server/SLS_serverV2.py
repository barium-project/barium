"""
### BEGIN NODE INFO
[info]
name = SLS Server
version = 1.0
description =
instancename = SLS Server
[startup]
cmdline = %PYTHON% %FILE%
timeout = 20
[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from labrad.types import Value
from labrad.devices import DeviceServer, DeviceWrapper
from labrad.server import setting, Signal
from twisted.internet.defer import inlineCallbacks, returnValue

TIMEOUT = Value(1.0, 's')

class SLS_device_wrapper(DeviceWrapper):

    @inlineCallbacks
    def connect(self, server, port):
        """Connect to a SLS laser controller device."""
        print 'connecting to "%s" on port "%s"...' % (server.name, port),
        self.server = server
        self.ctx = server.context()
        self.port = port
        p = self.packet()
        p.open(port)
        p.baudrate(115200)
        p.read()  # clear out the read buffer
        p.timeout(TIMEOUT)
        yield p.send()

    def packet(self):
        """Create a packet in our private context."""
        return self.server.packet(context=self.ctx)

    def shutdown(self):
        """Disconnect from the serial port when we shut down."""
        return self.packet().close().send()

    @inlineCallbacks
    def write(self, code):
        """Write a data value"""
        p = self.packet()
        p.write_line(code)
        yield p.send()

    @inlineCallbacks
    def read(self):
        """Read a line of data"""
        p = self.packet()
        p.read_line()
        ans = yield p.send()
        returnValue(ans.read_line)

    @inlineCallbacks
    def query(self, code):
        """ Write, then read. """
        p = self.packet()
        p.write_line(code)
        p.read_line()
        ans = yield p.send()
        returnValue(ans.read_line)

class SLS_Server(DeviceServer):
    name = 'SLS Server'
    deviceName = 'SLS Server'
    deviceWrapper = SLS_device_wrapper

    """
    Stable Laser Systems current controller, for 1762 laser and cavity.
    registry should contain a folder called 'settings' with 4 channel key value pairs ex.
    ucla_piezo_chan_4 (1.4V, false, 'name')
    
    """

    @inlineCallbacks
    def initServer(self):
        print 'loading config info...',
        self.reg = self.client.registry()
        yield self.loadConfigInfo()
        yield self.reg.cd(['', 'settings'], True)
        yield DeviceServer.initServer(self)


###Not sure what registry for SLS should be, is the registry like a place to put input settings?
    @inlineCallbacks
    def loadConfigInfo(self):
        """Load configuration information from the registry."""
        reg = self.reg
        yield reg.cd(['', 'Servers', 'SLS_Server', 'Links'], True)
        dirs, keys = yield reg.dir()
        p = reg.packet()
        for k in keys:
            p.get(k, key=k)
        ans = yield p.send()
        self.serialLinks = dict((k, ans[k]) for k in keys)

    @inlineCallbacks
    def findDevices(self):
        """Find available devices from list stored in the registry."""
        devs = []
        for name, (serServer, port) in self.serialLinks.items():
            if serServer not in self.client.servers:
                continue
            server = self.client[serServer]
            ports = yield server.list_serial_ports()
            if port not in ports:
                continue
            devName = '%s - %s' % (serServer, port)
            devs += [(devName, (server, port))]
        returnValue(devs)

    @setting(100, 'get_device_info')
    def get_device_info(self, c):
        dev = self.selectDevice(c)
        output = 'id?'
        yield dev.write(output)
        device_type = yield dev.read()
        device_id = yield dev.read()
        hardware_id = yield dev.read()
        firmware = yield dev.read()
        returnValue([device_type, device_id, hardware_id, firmware])


##New Functions for SLS
#Set the offset frequency of the SLS
    @setting(50, 'set_frequency', frequency = ['v[kHz]'])
    def set_frequency(self, c, chan, frequency):
        if frequency > self.max_frequency or frequency < self.min_frequency:
           returnValue('Frequency Range 20 MHz to 725 MHz')
        dev = self.selectDevice(c)
        output = 'set OffsetFrequency ' + str(frequency['kHz'])
        yield dev.write(output)        

    @setting(200,'get_frequency')
    def get_frequency(self, c):
        '''Set the offset frequency of the SLS'''
        dev = self.selectDevice(c)
        output = 'get OffsetFrequency\n\r'
        yield dev.write(output)        
        freq = yield dev.read() 
        freq= freq.split('\n')
        freq= freq[1][16:].split('E')
        freq= float(freq[0])*10**(float(freq[1][1:3]))
        returnValue(freq)
             
if __name__ == "__main__":
    from labrad import util
    util.runServer(SLS_Server())
