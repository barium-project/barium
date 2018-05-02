"""
### BEGIN NODE INFO
[info]
name = current_controller
version = 1.0
description =
instancename = current_controller

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

from labrad.types import Value
from labrad.devices import DeviceServer, DeviceWrapper
from labrad.server import setting
from twisted.internet.defer import inlineCallbacks, returnValue


class current_controller_wrapper(DeviceWrapper):

    @inlineCallbacks
    def connect(self, server, port):
        """Connect to a UCLA current controller."""
        print 'connecting to "%s" on port "%s"...' % (server.name, port),
        self.server = server
        self.ctx = server.context()
        self.port = port
        p = self.packet()
        p.open(port)
        p.baudrate(38400)
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
        """Write a data value to the heat switch."""
        yield self.packet().write(code).send()

    @inlineCallbacks
    def query(self, code):
        """ Write, then read. """
        p = self.packet()
        p.write_line(code)
        p.read_line()
        ans = yield p.send()
        returnValue(ans.read_line)


class current_controller_server(DeviceServer):
    name = 'current_controller'
    deviceWrapper = current_controller_wrapper

    @inlineCallbacks
    def initServer(self):
        self.output = None
        self.current = None
        print 'loading config info...',
        self.reg = self.client.registry()
        yield self.loadConfigInfo()
        print self.serialLinks
        yield DeviceServer.initServer(self)

    @inlineCallbacks
    def loadConfigInfo(self):
        """Load configuration information from the registry."""
        reg = self.reg
        yield reg.cd(['', 'Servers', 'current_controller', 'Links'], True)
        dirs, keys = yield reg.dir()
        p = reg.packet()
        for k in keys:
            p.get(k, key=k)
        ans = yield p.send()
        self.serialLinks = dict((k, ans[k]) for k in keys)
        # Get output state and last value of current set
        yield reg.cd(['', 'Servers', 'current_controller', 'parameters'], True)
        dirs, keys = yield reg.dir()
        p = reg.packet()
        for k in keys:
            p.get(k, key=k)
        ans = yield p.send()
        self.params = dict((k, ans[k]) for k in keys)
        try:
            self.output = bool(self.params['state'])
            self.current = self.params['current']
        except:
            print "Failed to load current controller state. Check Registry"


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

    @setting(100, value='v[mA]')
    def set_current(self, c, value):
        '''
        Sets the value of the current. Accepts mA.
        '''
        dev = self.selectDevice(c)
        yield dev.write('iout.w ' + str(int(value['uA']))+ '\r\n')
        yield self.reg.set('current',value)
        
    @setting(101, value='b')
    def set_output_state(self, c, value):
        '''
        Turn the current on or off
        '''
        self.output = value
        dev = self.selectDevice(c)
        yield dev.write('out.w ' + str(int(value))+ '\r\n')
        yield self.reg.set('state',int(value))

    @setting(200, returns='b')
    def get_output_state(self, c, value):
        '''
        Get the output state of the current controller. State is unkown when
        server is first started or restarted.
        '''
        try:
            if self.output == None:
                raise ValueError('Unknown output state')
        except ValueError as e:
                print e
            
        return self.output

    @setting(201, returns='v[mA]')
    def get_current(self, c):
        
        try:
            if self.current == None:
                raise ValueError('Unknown value of current')
        except ValueError as e:
                print e
        
        return self.current

TIMEOUT = Value(1, 's')

if __name__ == "__main__":
    from labrad import util
    util.runServer(current_controller_server())
