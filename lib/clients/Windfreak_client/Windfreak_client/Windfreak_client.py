from PyQt4 import QtGui
from twisted.internet.defer import inlineCallbacks, returnValue
import socket
import os
from barium.lib.clients.gui.Windfreak_gui import QWindfreakGui

SIGNALID1 = 445567

class Windfreak_client(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(Windfreak_client, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
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
                            + 'Windfreak Gui', password=self.password)
        self.reg = self.cxn.registry
        self.server = self.cxn.windfreak_server
        #self.set_up_channels()
        self.initializeGUI()
       


    @inlineCallbacks
    def initializeGUI(self):
        layout = QtGui.QGridLayout()
        qBox = QtGui.QGroupBox('Windfreak Gui')
        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        layout.addWidget(qBox, 0, 0), returnValue
        
        
        #yield self.reg.cd(['Clients','Fiber Switch Client'])
        #self.channel_list = yield self.reg.get('Channels')
        


        self.gui = QWindfreakGui()
            
        #init_chan = yield self.server.get_channel()
        #self.channel.displayChannel.setNum(int(init_chan))

            
        '''
        for now channels labels are stored in the registry as
        a list of 2-element arrays, i.e.,
        [['laser 1', channel num], ['laser 2', chan num], ...]
        stored in "registry/Clients/Fiber Switch Client"
        '''
        stateA = yield self.is_rf_A_on()
        print(stateA)
        if stateA:
            print("if")
            self.gui.rf_switch.setDown(True)
        stateB = yield self.is_rf_B_on()
        if stateB:
            self.gui.rf_switch2.setDown(True)
        
        self.gui.spinFreq.valueChanged.connect(lambda freqA = self.gui.spinFreq.value(),\
                                               : self.rf_freq_A(freqA))

        self.gui.rf_switch.clicked.connect(lambda stateA = self.gui.rf_switch.isDown(),\
                                           : self.rf_output_A(stateA))

        self.gui.spinFreq_.valueChanged.connect(lambda freqB = self.gui.spinFreq_.value(),\
                                               : self.rf_freq_B(freqB))

        self.gui.rf_switch2.clicked.connect(lambda stateB = self.gui.rf_switch2.isDown(),\
                                           : self.rf_output_B(stateB))

        
        self.gui.spinAmp.valueChanged.connect(lambda powerA = self.gui.spinAmp.value(),\
                                               : self.rf_pow_A(powerA))
        
        self.gui.spinAmp2.valueChanged.connect(lambda powerB = self.gui.spinAmp2.value(),\
                                               : self.rf_pow_B(powerB))             
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
    def rf_pow_A(self, num):
        yield self.server.set_channel(0)
        yield self.server.set_power(num)

    @inlineCallbacks
    def rf_pow_B(self, num):
        yield self.server.set_channel(1)
        yield self.server.set_power(num)

    @inlineCallbacks
    def rf_freq_A(self, num):
        yield self.server.set_channel(0)
        yield self.server.set_freq(num)
    @inlineCallbacks
    def rf_freq_B(self, num):
        yield self.server.set_channel(1)
        yield self.server.set_freq(num)

    @inlineCallbacks
    def rf_output_A(self,state):
        if state:
            yield self.server.set_channel(0)
            yield self.server.turn_on_rf()
        else:
            yield self.server.set_channel(0)
            yield self.server.turn_off_rf()
    @inlineCallbacks
    def rf_output_B(self,state):
        if state:
            yield self.server.set_channel(1)
            yield self.server.turn_on_rf()
        else:
            yield self.server.set_channel(1)
            yield self.server.turn_off_rf()

    @inlineCallbacks
    def is_rf_A_on(self):
        yield self.server.set_channel(0)
        state= yield self.server.is_rf_on()
        returnValue(state)

    @inlineCallbacks
    def is_rf_B_on(self):
        yield self.server.set_channel(1)
        state= yield self.server.is_rf_on()
        returnValue(state)


##    @inlineCallbacks
##    def rf_off_A(self):
##        yield self.server.set_channel("0")
##        yield self.server.turn_off_rf()
##    @inlineCallbacks
##    def rf_off_B(self):
##        yield self.server.set_channel("1")
##        yield self.server.turn_off_rf()


        
    
    


if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor  
    client_inst = Windfreak_client(reactor)
    client_inst.show()
    reactor.run()
