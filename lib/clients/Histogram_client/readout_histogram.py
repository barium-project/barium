from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
# this try and except avoids the error "RuntimeError: wrapped C/C++ object of type QWidget has been deleted"
try:
	from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
except:
	from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar


from matplotlib.figure import Figure
from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
import numpy, array
import time

class config_hist(object):
    #IDs for signaling
    ID_A = 99999
    ID_B = 99998
    #data vault comment
    dv_data_set = ['OpticalPumping','BrightState','D32_hist',\
                   'MicrowaveSweep_hist', 'Rabi_hist',\
                    'Ramsey_hist','metastable_prep_hist']
    #semaphore locations
    readout_threshold_dir =  ('StateReadout','state_readout_threshold')

class readout_histogram(QtGui.QWidget):
    def __init__(self, reactor, cxn = None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.reactor = reactor
        self.cxn = cxn
        self.thresholdVal = 10
        self.last_data = None
        self.last_hist = None
        self.last_fid = None
        self.current_data_set = 0
        self.subscribed = [False,False]
        self.create_layout()
        self.connect_labrad()

    def create_layout(self):
        layout = QtGui.QVBoxLayout()
        plot_layout = self.create_plot_layout()
        layout.addLayout(plot_layout)
        self.setLayout(layout)

    def create_plot_layout(self):
        layout = QtGui.QVBoxLayout()
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.axes = self.fig.add_subplot(211)
        self.axes.set_xlim(left = 0, right = 100)
        self.axes.set_ylim(bottom = 0, top = 50)
        self.thresholdLine = self.axes.axvline(self.thresholdVal, linewidth=3.0, color = 'r', label = 'Threshold')
        self.axes.legend(loc = 'best')
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        self.axes.set_title('State Readout', fontsize = 22)
        self.axes1 = self.fig.add_subplot(212)
        self.axes1.set_xlim(left = 0, right = 10)
        self.axes1.set_ylim(bottom = 0, top = 1.1)
        self.fig.tight_layout()
        layout.addWidget(self.mpl_toolbar)
        layout.addWidget(self.canvas)
        return layout

    def connect_layout(self):
        self.canvas.mpl_connect('button_press_event', self.on_key_press)

    @inlineCallbacks
    def on_key_press(self, event):
        if event.button == 2:
            xval = int(round(event.xdata))
            yield self.thresholdChange(xval)

    def on_new_data(self, readout):
        self.last_data = readout
        self.current_data_set  = self.current_data_set + 1
        self.update_histogram(readout)
        self.plot_fidelity()

    def update_histogram(self, data):
        #remove old histogram
        if self.last_hist is not None:
            self.last_hist.remove()
            #explicitly delete the reference although not necessary
            #el self.last_hist
        y = numpy.histogram(data[:,-1],int(numpy.max([data[:,-1].max()-data[:,-1].min(),1])))
        counts = y[0]
        bins = y[1][:-1]
        if bins[0] < 0:
        	bins = bins + .5
        self.last_hist = self.axes.bar(bins, counts, width = 1)
        x_maximum = bins.max()
        x_min = bins.min()
        self.axes.set_xlim(left = int(x_min - 2))
        self.axes.set_xlim(right = int(x_maximum+2))
        self.axes.set_ylim(bottom = 0)
        y_maximum = counts.max()
        self.axes.set_ylim(top = y_maximum+1)
        self.canvas.draw()


    def plot_fidelity(self):
    	# check xaxis
        x_max = self.axes1.get_xlim()[1]
        if self.current_data_set == x_max-2:
            self.axes1.set_xlim(right = x_max+1)
        bright = numpy.where(self.last_data[:,1] >= self.thresholdVal)
        fid = float(len(bright[0]))/len(self.last_data[:,1])
        self.last_fid  = self.axes1.plot(self.current_data_set,fid,'o')
        self.canvas.draw()

    def update_fidelity(self):
    	if self.last_fid is not None:
    		self.axes1.lines[self.current_data_set - 1].remove()

        if self.last_data is not None:
            bright = numpy.where(self.last_data[:,1] >= self.thresholdVal)
            fid = float(len(bright[0]))/len(self.last_data[:,1])
            self.last_fid  = self.axes1.plot(self.current_data_set,fid,'o')
            self.canvas.draw()


    @inlineCallbacks
    def thresholdChange(self, threshold):
        #update canvas
        self.update_canvas_line(threshold)
        self.thresholdVal = threshold
        self.update_fidelity()
        try:
            server = yield self.cxn.get_server('ParameterVault')
            yield server.set_parameter(config_hist.readout_threshold_dir[0], config_hist.readout_threshold_dir[1], threshold, context = self.context)
        except Exception, e:
            print e
            yield None

    def update_canvas_line(self, threshold):
        self.thresholdLine.remove()
        #explicitly delete the refrence although not necessary
        del self.thresholdLine
        try:
            self.thresholdLine = self.axes.axvline(threshold, ymin=0.0, ymax=100.0, linewidth=3.0, color = 'r', label = 'Threshold')
        except Exception as e:
            #drawing axvline throws an error when the plot is never shown (i.e in different tab)
            print 'Weird singular matrix bug deep inside matplotlib'
        self.canvas.draw()

    @inlineCallbacks
    def connect_labrad(self):
        if self.cxn is None:
            from common.lib.clients import connection
            self.cxn = connection.connection()
            yield self.cxn.connect()
        self.context = yield self.cxn.context()
        try:
            yield self.subscribe_data_vault()
        except Exception,e:
            print e
            self.setDisabled(True)
        try:
            yield self.subscribe_parameter_vault()
        except Exception, e:
            print e
            print 'Not Initially Connected to ParameterVault', e
            self.setDisabled(True)
        yield self.cxn.add_on_connect('Data Vault', self.reinitialize_data_vault)
        yield self.cxn.add_on_connect('ParameterVault', self.reinitialize_parameter_vault)
        yield self.cxn.add_on_disconnect('ParameterVault', self.disable)
        yield self.cxn.add_on_disconnect('Data Vault', self.disable)
        self.connect_layout()

    @inlineCallbacks
    def subscribe_data_vault(self):
        dv = yield self.cxn.get_server('Data Vault')
        yield dv.signal__new_parameter_dataset(config_hist.ID_A, context = self.context)
        yield dv.addListener(listener = self.on_new_dataset, source = None, ID = config_hist.ID_A, context = self.context)
        self.subscribed[0] = True


    @inlineCallbacks
    def subscribe_parameter_vault(self):
        server = yield self.cxn.get_server('ParameterVault')
        yield server.signal__parameter_change(config_hist.ID_B, context = self.context)
        yield server.addListener(listener = self.on_parameter_change, source = None, ID = config_hist.ID_B, context = self.context)
        init_val = yield server.get_parameter(config_hist.readout_threshold_dir[0],config_hist.readout_threshold_dir[1], context = self.context)
        self.update_canvas_line(init_val)
        self.subscribed[1] = True

    @inlineCallbacks
    def reinitialize_data_vault(self):
        self.setDisabled(False)
        server = yield self.cxn.get_server('Data Vault')
        yield server.signal__new_parameter_dataset(config_hist.ID_A, context = self.context)
        if not self.subscribed[0]:
            yield server.addListener(listener = self.on_new_dataset, source = None, ID = config_hist.ID_A, context = self.context)
            self.subscribed[0] = True

    @inlineCallbacks
    def reinitialize_parameter_vault(self):
        self.setDisabled(False)
        server = yield self.cxn.get_server('ParameterVault')
        yield server.signal__parameter_change(config_hist.ID_B, context = self.context)
        if not self.subscribed[1]:
            yield server.addListener(listener = self.on_parameter_change, source = None, ID = config_hist.ID_B, context = self.context)
            self.subscribed[1] = True
        init_val = yield server.get_parameter(config_hist.readout_threshold_dir[0],config_hist.readout_threshold_dir[1], context = self.context)
        self.update_canvas_line(init_val)

    @inlineCallbacks
    def disable(self):
        self.setDisabled(True)
        yield None

    @inlineCallbacks
    def on_parameter_change(self, signal, parameter_id):
        if parameter_id == config_hist.readout_threshold_dir:
            server = yield self.cxn.get_server('ParameterVault')
            init_val = yield server.get_parameter(config_hist.readout_threshold_dir[0],config_hist.readout_threshold_dir[1], context = self.context)
            self.update_canvas_line(init_val)

    @inlineCallbacks
    def on_new_dataset(self, x, y):
    	# To only plot the latest histogram, the string in the added datavault param
    	# has the number of cycles for that experiment at the end
    	if y[3][:4] == 'hist':
            dv = yield self.cxn.get_server('Data Vault')
            ind = y[3].index('c')
            num = int(y[3][(ind+1):])
            dataset = y[0]
            directory = y[2]
            yield dv.cd(directory, context = self.context)
            yield dv.open(dataset, context = self.context)
            data = yield dv.get(context = self.context)
            data = data[-num:]
            yield deferToThread(self.on_new_data, data)
            yield dv.cd([''], context = self.context)

    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = readout_histogram(reactor)
    widget.show()
    reactor.run()
