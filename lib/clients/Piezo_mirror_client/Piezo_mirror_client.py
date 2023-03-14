from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks, returnValue
import socket
import os
from barium.lib.clients.gui.piezo_mirror_gui import QPiezoMirrorGui
from config.multiplexerclient_config import multiplexer_config

#from labrad.units import WithUnit as U


SIGNALID1 = 445571
SIGNALID2 = 445572
SIGNALID3 = 445573
SIGNALID4 = 445574

class Piezomirror_client(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(Piezomirror_client, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        print("b")

        self.reactor = reactor
        self.channel = {}
        self.channel_GUIs = {}
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to the wavemeter computer and
        connects incoming signals to relavent functions (((which computer???)))
        """
        from labrad.wrappers import connectAsync
        self.password = os.environ['LABRADPASSWORD']
        self.cxn = yield connectAsync('localhost', name = socket.gethostname()\
                            + 'Piezo_Mirror Gui', password=self.password)
        self.reg = self.cxn.registry
        self.server = yield self.cxn.piezo_controller
        
        #self.set_up_channels()
        self.initializeGUI()
       


    @inlineCallbacks
    def initializeGUI(self):
        layout = QtGui.QGridLayout()
        qBox = QtGui.QGroupBox('Piezo Mirror Gui')
        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        layout.addWidget(qBox, 0, 0), returnValue
        
        
        #yield self.reg.cd(['Clients','Fiber Switch Client'])
        #self.channel_list = yield self.reg.get('Channels')
        


        self.gui = QPiezoMirrorGui()
            
        #init_chan = yield self.server.get_channel()
        #self.channel.displayChannel.setNum(int(init_chan))

            
        '''
        for now channels labels are stored in the registry as
        a list of 2-element arrays, i.e.,
        [['laser 1', channel num], ['laser 2', chan num], ...]
        stored in "registry/Clients/Fiber Switch Client"
        '''
##        stateA = yield self.is_rf_A_on()
##        print(stateA)
##        if stateA:
##            print("if")
##            self.gui.rf_switch.setDown(True)
##        stateB = yield self.is_rf_B_on()
##        if stateB:
##            self.gui.rf_switch2.setDown(True)
        
        self.gui.SpinVoltage.valueChanged.connect(lambda Voltage1 = self.gui.SpinVoltage.value(),\
                                               : self.set_dac_voltage(1,Voltage1))

        self.gui.SpinVoltage2.valueChanged.connect(lambda Voltage2 = self.gui.SpinVoltage2.value(),\
                                               : self.set_dac_voltage(2,Voltage2))

        self.gui.SpinVoltage3.valueChanged.connect(lambda Voltage3 = self.gui.SpinVoltage3.value(),\
                                               : self.set_dac_voltage(3,Voltage3))

        self.gui.SpinVoltage4.valueChanged.connect(lambda Voltage4 = self.gui.SpinVoltage3.value(),\
                                               : self.set_dac_voltage(4,Voltage4))
        
        self.gui.volt_switch.clicked.connect(lambda state1 = self.gui.volt_switch.isDown(),\
                                           : self.set_state(1,state1))

        self.gui.volt_switch2.clicked.connect(lambda state2 = self.gui.volt_switch2.isDown(),\
                                           : self.set_state(2,state2))

        self.gui.volt_switch3.clicked.connect(lambda state3 = self.gui.volt_switch3.isDown(),\
                                           : self.set_state(3,state3))
        self.gui.volt_switch4.clicked.connect(lambda state4 = self.gui.volt_switch4.isDown(),\
                                           : self.set_state(4,state4))

                  
##        self.channel.checkChannel.clicked.connect(lambda: self.refreshNum())
##    
##        
###        print(channel1[0])
##        self.channel.c1label.setText(str(self.channel_list[0][0]) + ' nm')
##        self.channel.c2label.setText(str(self.channel_list[1][0]) + ' nm')
##        self.channel.c3label.setText(str(self.channel_list[2][0]) + ' nm')
##        self.channel.c4label.setText(str(self.channel_list[3][0]) + ' nm')
##        self.channel.c5label.setText(str(self.channel_list[4][0]) + ' nm')
##        self.channel.c6label.setText(str(self.channel_list[5][0]) + ' nm')
##        self.channel.c7label.setText(str(self.channel_list[6][0]) + ' nm')
##        self.channel.c8label.setText(str(self.channel_list[7][0]) + ' nm')
##            
##
##        #self.channel_GUIs[chan] = laser
        subLayout.addWidget(self.gui, 1, 1)
        layout.minimumSize()
        self.setLayout(layout)

    @inlineCallbacks
    def set_state(self, chan,value):
        yield self.server.set_output_state(chan,value)
    @inlineCallbacks
    def set_dac_voltage(self, chan, voltage):
        #self.lasers[chan][7] = voltage
        yield self.server.set_dac_voltage(chan,voltage)

##    @inlineCallbacks
##    def rf_freq_A(self, num):
##        yield self.server.set_channel(0)
##        yield self.server.set_freq(num)
##    @inlineCallbacks
##    def rf_freq_B(self, num):
##        yield self.server.set_channel(1)
##        yield self.server.set_freq(num)
##
##    @inlineCallbacks
##    def rf_output_A(self,state):
##        if state:
##            yield self.server.set_channel(0)
##            yield self.server.turn_on_rf()
##        else:
##            yield self.server.set_channel(0)
##            yield self.server.turn_off_rf()
##    @inlineCallbacks
##    def rf_output_B(self,state):
##        if state:
##            yield self.server.set_channel(1)
##            yield self.server.turn_on_rf()
##        else:
##            yield self.server.set_channel(1)
##            yield self.server.turn_off_rf()
##
##    @inlineCallbacks
##    def is_rf_A_on(self):
##        yield self.server.set_channel(0)
##        state= yield self.server.is_rf_on()
##        returnValue(state)
##
##    @inlineCallbacks
##    def is_rf_B_on(self):
##        yield self.server.set_channel(1)
##        state= yield self.server.is_rf_on()
##        returnValue(state)


##    @inlineCallbacks
##    def rf_off_A(self):
##        yield self.server.set_channel("0")
##        yield self.server.turn_off_rf()
##    @inlineCallbacks
##    def rf_off_B(self):
##        yield self.server.set_channel("1")
##        yield self.server.turn_off_rf()


        
    
    


if __name__ == "__main__":
    b = QtGui.QApplication( [] )
    print("a")
    import qt4reactor
    print("C")
    qt4reactor.install()
    from twisted.internet import reactor  
    piezo_client = Piezomirror_client(reactor)
    piezo_client.show()
    reactor.run()
