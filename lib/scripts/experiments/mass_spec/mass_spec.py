import labrad
from labrad.units import WithUnit as U
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from twisted.internet.defer import inlineCallbacks, returnValue
import numpy as np
import time, os
import datetime as datetime


class mass_spec(experiment):

    name = 'Mass Spec'

    exp_parameters = []

    exp_parameters.append(('Mass_Spec', 'Mass'))
    exp_parameters.append(('Mass_Spec', 'High_Voltage'))
    exp_parameters.append(('Mass_Spec', 'Filament'))
    exp_parameters.append(('Mass_Spec', 'Records_Per_Scan'))
    exp_parameters.append(('Mass_Spec', 'Discriminator'))
    exp_parameters.append(('Mass_Spec', 'Current'))
    exp_parameters.append(('Mass_Spec', 'Count_Time'))

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'Mass Spec')
        self.rga_cxn = labrad.connect('flexo', password = 'lab')
        self.rga = self.rga_cxn.rga_server
        self.scalar = self.cxn.sr430_scalar_server
        self.scalar.select_device(0)
        self.dv = self.cxn.data_vault
        self.grapher = self.cxn.real_simple_grapher

        self.p = self.parameters.Mass_Spec

    def run(self, cxn, context):
        self.set_up_parameters()
        self.set_up_datavault()
        self.set_up_devices()

        for i in range(self.num_steps):
            if self.pause_or_stop():
                break

            self.rga.mass_lock(self.mass[i])
            self.scalar.clear_scan()
            self.scalar.start_scan()
            time.sleep(self.count)
            counts = self.scalar.get_counts()
            time.sleep(1)
            print self.mass[i],counts
            self.dv.add(self.mass[i],counts)


    def set_up_datavault(self):
        # set up folder
        date = datetime.datetime.now()
        year  = `date.year`
        month = '%02d' % date.month  # Padded with a zero if one digit
        day   = '%02d' % date.day    # Padded with a zero if one digit
        trunk = year + '_' + month + '_' + day
        self.dv.cd(['',year,month,trunk],True)
        dataset = self.dv.new('Mass_Spec', [('Mass', 'amu')], [('', 'Counts', 'a.b.u')])
        self.grapher.plot(dataset,'Mass_Spec', False)

        # add dv params
        self.dv.add_parameter('High Voltage', self.p.High_Voltage)
        self.dv.add_parameter('Current', self.p.Current)
        self.dv.add_parameter('Filament', self.p.Filament)
        self.dv.add_parameter('Records Per Scan', self.p.Records_Per_Scan)
        self.dv.add_parameter('Discriminator', self.p.Discriminator)
        self.dv.add_parameter('Count Time', self.p.Count_Time)

    def set_up_parameters(self):
        self.current = self.p.Current['A']
        self.voltage = self.p.High_Voltage['V']
        self.filament = self.p.Filament
        self.records = self.p.Records_Per_Scan
        self.discriminator = self.p.Discriminator
        self.count = self.p.Count_Time['s']

        self.min_mass = self.p.Mass[0]['amu']
        self.max_mass = self.p.Mass[1]['amu']
        self.num_steps = self.p.Mass[2]
        self.mass = np.linspace(self.min_mass,self.max_mass,self.num_steps)
        print self.num_steps

    def set_up_devices(self):
        self.rga.high_voltage(1000)
        time.sleep(2)
        self.rga.high_voltage(int(self.voltage))
        time.sleep(1)
        if int(self.filament) == 1:
            self.rga.filament(1)
            time.sleep(1)
        self.scalar.records_per_scan(int(self.records))
        self.scalar.discriminator_level(self.discriminator)


    def finalize(self, cxn, context):
        self.rga.high_voltage(0)
        time.sleep(1)
        if int(self.filament)==1:
            self.rga.filament(0)
            time.sleep(1)
        self.cxn.disconnect()
        self.rga_cxn.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = mass_spec(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)


