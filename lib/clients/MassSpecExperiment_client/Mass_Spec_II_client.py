# Copyright (C) 2016 Calvin He
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

# This project was started but not finished.

from barium.lib.clients.gui.MassSpecExperiment_II_gui import Ui_Form

from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui, QtCore
import numpy as np
import ctypes
from datetime import datetime

class Mass_Spec_II_Client(Ui_Form):
    def __init__(self, reactor, parent = None):
        super(Mass_Spec_II_Client, self).__init__()
        
    def signal_connect(self):
        self.frame_1.setDisabled(True)
        self.frame_2.setDisabled(True)
        self.connect_button.clicked.connect(lambda: self.labrad_connect())
        self.add_scan_button.clicked.connect(lambda : self.add_scan())
        self.add_repeat_button.clicked.connect(lambda: self.add_repeat())
        self.add_new_datarun_button.clicked.connect(lambda: self.add_new_datarun())
        self.delete_button.clicked.connect(lambda :self.delete())
        self.load_button.clicked.connect(lambda :self.load())
        self.save_button.clicked.connect(lambda :self.save())
        self.experiment_tree.itemSelectionChanged.connect(lambda :self.select_item())
        self.move_up_button.clicked.connect(lambda :self.move_up())
        self.move_down_button.clicked.connect(lambda :self.move_down())
        self.clear_button.clicked.connect(lambda :self.clear())
        

    @inlineCallbacks
    def labrad_connect(self):
        from labrad.wrappers import connectAsync
        host = str(self.host_name_combobox.currentText())
        self.cxn = yield connectAsync(host, name="Mass Spectrum II Client", password="lab")
        self.hp_id = self.hp_id_spinbox.value()
        self.sca_id = self.sca_id_spinbox.value()

        #self.hpserver = self.cxn.hp6033a_server
        #self.hpserver.select_device(self.hp_id)
        #self.scaserver = self.cxn.sr430_scalar_server
        #self.scaserver.select_device(self.hp_id)
        #self.rgaserver = self.cxn.rga_server

        self.frame_1.setDisabled(False)
        self.frame_2.setDisabled(False)
        self.frame.setDisabled(True)

    @inlineCallbacks
    def select_item(self):
        if len(self.experiment_tree.selectedItems())>0:
            selected_item = self.experiment_tree.selectedItems()[0]
            parent = selected_item.parent()
            if parent == None:
                index =  self.experiment_tree.indexOfTopLevelItem(selected_item)
                has_parent = 'Parent'
            else:
                index = parent.indexOfChild(self.experiment_tree.selectedItems()[0])
                has_parent = 'Child'
            print selected_item, index, has_parent
            yield None

    @inlineCallbacks
    def add_scan(self):
        mass = int(self.scan_table.item(0,0).text())
        discriminator_level = int(self.scan_table.item(0,1).text())
        current = int(self.scan_table.item(0,2).text())
        filament_state = int(self.scan_table.item(0,3).text())
        filament_voltage = int(self.scan_table.item(0,4).text())
        records_per_scan = int(self.scan_table.item(0,5).text())

        parameter_list = [mass, discriminator_level, current, filament_state, filament_voltage, records_per_scan]
        if len(self.experiment_tree.selectedItems())>0:
            selected_item = self.experiment_tree.selectedItems()[0]
            parent = selected_item.parent()
            item = QtGui.QTreeWidgetItem()
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            item.setText(0,str(parameter_list))
            if parent == None:
                selected_item.addChild(item)
                self.experiment_tree.expandItem(selected_item)
            else:
                index = parent.indexOfChild(selected_item)
                parent.insertChild(index, item)
                self.experiment_tree.expandItem(parent)
        else:
            print 'No datarun selected.'
        yield None

    @inlineCallbacks
    def add_repeat(self):
        item = QtGui.QTreeWidgetItem()
        repetitions = self.repetitions_spinbox.value()
        item.setText(0,"Repeat Last Datarun ["+str(repetitions)+"]")
        if len(self.experiment_tree.selectedItems())>0:
            index = self.experiment_tree.indexOfTopLevelItem(self.experiment_tree.selectedItems()[0])
        else:
            index = 0
        self.experiment_tree.insertTopLevelItem(index, item)
        yield None

    @inlineCallbacks
    def add_new_datarun(self):
        item = QtGui.QTreeWidgetItem()
        if len(self.experiment_tree.selectedItems())>0:
            selected_item = self.experiment_tree.selectedItems()[0]
            parent = selected_item.parent()
            if parent == None:
                index = self.experiment_tree.indexOfTopLevelItem(self.experiment_tree.selectedItems()[0])
            else:
                index = self.experiment_tree.indexOfTopLevelItem(parent)
        else:
            index = 0
        item.setText(0,"Datarun [ml, dl, c, fl, hv, rps]")
        self.experiment_tree.insertTopLevelItem(index, item)
        yield None

    @inlineCallbacks
    def delete(self):
        if len(self.experiment_tree.selectedItems())>0:
            selected_item = self.experiment_tree.selectedItems()[0]
            parent = selected_item.parent()
            if parent == None:
                index = self.experiment_tree.indexOfTopLevelItem(selected_item)
                self.experiment_tree.takeTopLevelItem(index)
            else:
                index = parent.indexOfChild(selected_item)
                parent.takeChild(index)
        else:
            print 'No datarun selected.'
        yield None

    @inlineCallbacks
    def clear(self):
        self.experiment_tree.clear()
        yield None
    
    @inlineCallbacks
    def move_up(self):
        selected_item = self.experiment_tree.selectedItems()[0]
        parent = selected_item.parent()
        if self.experiment_tree.itemAbove(selected_item) == None:
            pass
        else:
            item_above = self.experiment_tree.itemAbove(selected_item)
            if parent == None:
                index = self.experiment_tree.indexOfTopLevelItem(item_above)
                self.experiment_tree.takeTopLevelItem(index)
                self.experiment_tree.insertTopLevelItem(index+1, item_above)
            else:
                index = parent.indexOfChild(item_above)
                parent.takeChild(index)
                parent.insertChild(index+1, item_above)
        yield None

    @inlineCallbacks
    def move_down(self):
        selected_item = self.experiment_tree.selectedItems()[0]
        parent = selected_item.parent()
        if self.experiment_tree.itemBelow(selected_item) == None:
            pass
        else:
            item_below = self.experiment_tree.itemBelow(selected_item)
            if parent == None:
                index = self.experiment_tree.indexOfTopLevelItem(item_below)
                self.experiment_tree.takeTopLevelItem(index)
                self.experiment_tree.insertTopLevelItem(index-1, item_below)
            else:
                index = parent.indexOfChild(item_below)
                parent.takeChild(index)
                parent.insertChild(index-1, item_below)
        yield None

    @inlineCallbacks
    def load(self):
        dialog = QtGui.QFileDialog()
        dialog.setDirectory('C:\Users\barium133\Code\barium\lib\clients\MassSpecExperiment_client')
        filepath = str(dialog.getOpenFileName())
        settings = np.loadtxt(filepath,dtype=str,delimiter='\n')
        print settings
        yield None

    @inlineCallbacks
    def save(self):
        dialog = QtGui.QFileDialog()
        dialog.setDirectory('C:\Users\barium133\Code\barium\lib\clients\MassSpecExperiment_client')
        filepath = str(dialog.getSaveFileName())
        print filepath
        number_of_dataruns = self.experiment_tree.topLevelItemCount()
        array=[]
        for i in range(number_of_dataruns):
            datarun = self.experiment_tree.topLevelItem(i)
            number_of_scans = datarun.childCount()
            print datarun.text(0)
            line = []
            line.append(str(datarun.text(0)))
            for j in range(number_of_scans):
                scan = datarun.child(j)
                print scan.text(0)
                line.append(str(scan.text(0)))
            array.append(line)
        np.savetxt(filepath,array,fmt='%s')
        yield None

    @inlineCallbacks
    def closeEvent(self, x):
        reactor.stop()
        yield None


import sys

if __name__ == "__main__":
    a = QtGui.QApplication ([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    client = Mass_Spec_II_Client(reactor)
    widget = QtGui.QWidget()
    client.setupUi(widget)
    client.signal_connect()
    widget.show()

    reactor.run()
    
    sys.exit(a.exec_())
