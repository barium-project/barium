import labrad
from labrad.units import WithUnit
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
import datetime as datetime
from twisted.internet.defer import inlineCallbacks, returnValue
import numpy as np

class linescan_camera(experiment):

    name = 'Linescan Camera'

    exp_parameters = []

    exp_parameters.append(('Linescan_Camera', 'lasername'))

    exp_parameters.append(('Linescan_Camera', 'Center_Frequency_493'))
    exp_parameters.append(('Linescan_Camera', 'Center_Freqeuncy_650'))

    exp_parameters.append(('Linescan_Camera', 'wm_channel_493'))
    exp_parameters.append(('Linescan_Camera', 'wm_channel_493'))



    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'Linescan Camera')
        self.cxnwlm = labrad.connect('10.97.111.8', name = 'Linescan Camera', password = 'lab')
        self.dv = self.cxn.data_vault
        self.grapher = self.cxn.grapher
        self.cam = self.cxn.andor_server


        self.laser = self.parameters.Linescan_Camera.lasername

        if self.laser == '493':
            self.port = self.parameters.Linescan_Camera.wm_channel_493
            self.centerfrequency = \
                self.parameters.Linescan_Camera.Center_Frequency_493

        elif self.laser == '650':
            self.port = self.parameters.Linescan_Camera.Port_650
            self.centerfrequency = \
                self.parameters.Linescan_Camera.Center_Frequency_650


    def run(self, cxn, context):
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day
        self.dv.cd(['',year,month,trunk],True)
        dataset = self.dv.new('Linescan Camera',[('freq', 'Hz')], [('', 'Amplitude','a.b.u.')])
        self.grapher.plot(dataset, 'spectrum', False)

        self.dv.add_parameter('Frequency', self.centerfrequency)
        self.dv.add_parameter('Laser', self.laser)
        self.dv.add_parameter('Center_Frequency_650', self.parameters.Linescan_Camera.Center_Frequency_650)

        self.currentfreq = self.currentfrequency()
        tempdata = []

        # Set cam paramters
        self.cam.set_acquisition_mode('Run till abort')
        self.cam.set_shutter_mode('Open')
        self.binx, self.biny, self.startx, self.stopx, self.starty, self.stopy = self.cam.get_image_region(None)
        self.pixels_x = (self.stopx - self.startx + 1) / self.binx
        self.pixels_y = (self.stopy - self.starty + 1) / self.biny
        self.cam.start_acquisition(None)

        while True:
            should_stop = self.pause_or_stop()
            if should_stop:
                tempdata.sort()
                self.dv.add(tempdata)
                self.cam.abort_acquisition()
                self.cam.set_shutter_mode('Close')

                break
            self.cam.wait_for_acquisition()
            image = self.cam.get_most_recent_image(None)
            image_data = np.reshape(image, (self.pixels_y, self.pixels_x))
            counts = np.sum(np.sum(image_data))
            self.currentfrequency()
            if self.currentfreq and counts:
                tempdata.append([self.currentfreq['GHz'], counts])




    def currentfrequency(self):
        absfreq = WithUnit(float(self.wm.get_frequency(self.port)), 'THz')
        self.currentfreq = absfreq - self.centerfrequency

    def finalize(self, cxn, context):
        self.cxn.disconnect()
        self.cxnwlm.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = linescan_camera(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




