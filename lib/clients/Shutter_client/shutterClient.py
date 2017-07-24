from barium.lib.clients.gui.shutter import QCustomSwitchChannel
from twisted.internet.defer import inlineCallbacks
from common.lib.clients.connection import connection
from PyQt4 import QtGui

from config.shutter_client_config import shutter_config


class shutterclient(QtGui.QWidget):

    def __init__(self, reactor, cxn=None):
        """initializes the GUI creates the reactor
            and empty dictionary for channel widgets to
            be stored for iteration. also grabs chan info
            from switch_config file
        """
        super(shutterclient, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.cxn = cxn
        self.d = {}
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates a connection if no connection passed and
        checked for saved switch settings

        """
        if self.cxn is None:
            self.cxn = connection(name="Shutter Client")
            yield self.cxn.connect()
        self.server = yield self.cxn.get_server('arduinottl')
        self.reg = yield self.cxn.get_server('registry')

        try:
            yield self.reg.cd(['', 'settings'])
            self.settings = yield self.reg.dir()
            self.settings = self.settings[1]
        except:
            self.settings = []

        self.chaninfo = shutter_config.info
        self.initializeGUI()

    @inlineCallbacks
    def initializeGUI(self):

        layout = QtGui.QGridLayout()

        qBox = QtGui.QGroupBox('Laser Shutters')
        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        layout.addWidget(qBox, 0, 0)

        for chan in self.chaninfo:
            port = self.chaninfo[chan][0]
            position = self.chaninfo[chan][1]
            inverted = self.chaninfo[chan][2]
            enable = self.chaninfo[chan][3]

            widget = QCustomSwitchChannel(chan, ('Closed', 'Open'))
            if chan + 'shutter' in self.settings:
                value = yield self.reg.get(chan + 'shutter')
                widget.TTLswitch.setChecked(bool(value))
            else:
                widget.TTLswitch.setChecked(False)

            widget.TTLswitch.toggled.connect(lambda state=widget.TTLswitch.isDown(),
                                             port=port, chan=chan, inverted=inverted:
                                             self.changeState(state, port, chan, inverted))

            widget.enableSwitch.clicked.connect(lambda state=widget.enableSwitch.isChecked(),
                                             port=enable, chan=chan, inverted=inverted:
                                             self.changeState(state, port, chan, inverted))

            self.d[port] = widget
            subLayout.addWidget(self.d[port], position[0], position[1])

        self.setLayout(layout)

    @inlineCallbacks
    def changeState(self, state, port, chan, inverted):
        if chan + 'shutter' in self.settings:
            yield self.reg.set(chan + 'shutter', state)
        if inverted:
            state = not state
        yield self.server.ttl_output(port, state)

    def closeEvent(self, x):
        self.reactor.stop()


if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    shutterWidget = shutterclient(reactor)
    shutterWidget.show()
    reactor.run()
