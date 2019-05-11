# Copyright 2014-2016 The Piccolo Team
#
# This file is part of piccolo3-utils.
#
# piccolo3-utils is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# piccolo3-utils is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with piccolo3-utils.  If not, see <http://www.gnu.org/licenses/>.

__all__ = ['main']

from PyQt5 import QtCore, QtGui, QtWidgets
from . import calibrate_ui

class SpectralLinesDelegate(QtWidgets.QItemDelegate):

    def __init__(self,parent,data,lightsource):
        self.pdata = data
        QtWidgets.QItemDelegate.__init__(self, parent)
        self.lightsource = lightsource


    def createEditor(self, parent, option, index):
        combo = QtWidgets.QComboBox(parent)
        li = ['-1']
        for l in self.pdata.spectralLines[self.lightsource].lines:
            li.append(str(l))
        combo.addItems(li)
        combo.setCurrentText(index.model().data(index))
        return combo
        
    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText())
        
    @QtCore.pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())

class Peaks(QtGui.QStandardItemModel):
    def __init__(self,*args,**keywords):
        self.pdata = keywords['data']
        del keywords['data']
        
        QtGui.QStandardItemModel.__init__(self,*args,**keywords)

    def selectLightSource(self,lightsource):
        peaks = self.pdata.peaks[self.pdata.peaks.lightSource==lightsource]
        self.clear()
        self.setHorizontalHeaderLabels(['pixel','wavelength','spectral line'])
        self.setColumnCount(3)
        self.setRowCount(len(peaks))

        i = 0
        for pixel,row in peaks.iterrows():
            item = QtGui.QStandardItem(str(pixel))
            item.setEditable(False)
            self.setItem(i,0,item)
            item = QtGui.QStandardItem(str(self.pdata.newWavelength(pixel)))
            item.setEditable(False)
            self.setItem(i,1,item)
            item = QtGui.QStandardItem(str(row.wavelength))
            self.setItem(i,2,item)
            i = i+1

    def highlightWavelength(self,wavelength):
        for r in range(self.rowCount()):
            if abs(float(self.item(r,1).text())-wavelength) < 1e-8:
                self.item(r,1).setForeground(QtGui.QBrush(QtGui.QColor('green')))
            else:
                self.item(r,1).setForeground(QtGui.QBrush(QtGui.QColor('black')))

    def setData(self,index,data):
        pixel = int(self.item(index.row(),column=0).text())
        QtGui.QStandardItemModel.setData(self,index,data)
        self.pdata.peaks.loc[pixel].wavelength = float(data)

class Coeffs(QtGui.QStandardItemModel):
    def __init__(self,*args,**keywords):
        self.pdata = keywords['data']
        del keywords['data']
        QtGui.QStandardItemModel.__init__(self,*args,**keywords)
        
        self.updateData()
        
    def updateData(self):
        self.clear()
        coeff = self.pdata.newCoeff
        self.setRowCount(1)
        self.setColumnCount(len(coeff))
        for i in range(len(coeff)):
            item = QtGui.QStandardItem(str(coeff[i]))
            item.setEditable(False)
            self.setItem(0,i,item)
        
class CalibrateApp(QtWidgets.QMainWindow, calibrate_ui.Ui_MainWindow):
    def __init__(self, calibrationData, parent=None):
        super(CalibrateApp, self).__init__()
        self.setupUi(self)

        self.calibrationData = calibrationData
        self.calibratePlot.data = calibrationData
        self.peaks = Peaks(data=self.calibrationData)
        self.coeff = Coeffs(data=self.calibrationData)
        
        self.calibratePlot.setCallback(self.peaks.highlightWavelength)
        
        # the light source selector
        self.lightSourceSelector.addItems(self.calibrationData.lightsources)
        self.lightSourceSelector.currentIndexChanged.connect(self.lightsourceChanged)

        # the peaks table
        self.tableView.setModel(self.peaks)

        # the coeff view
        self.coeffView.setModel(self.coeff)

        # hook up polyorder
        self.order = None
        self.changeOrder()
        self.polynomialOrder.editingFinished.connect(self.changeOrder)

        # the calculate button
        self.calculateCoeffs.clicked.connect(self.fitWavelengths)
        
        # set the light source
        self.lightsourceChanged()

        # fit the data
        self.fitWavelengths()

    def lightsourceChanged(self):
        ls = self.lightSourceSelector.currentText()
        self.calibratePlot.plotData(ls)
        self.peaks.selectLightSource(ls)
        self.tableView.setItemDelegateForColumn(2, SpectralLinesDelegate(self,self.calibrationData,ls))

    def changeOrder(self):
        self.order = self.polynomialOrder.value()
        
    def fitWavelengths(self):
        ls = self.lightSourceSelector.currentText()
        self.calibrationData.fitWavelength(order=self.order)
        self.calibratePlot.plotData(ls)
        self.coeff.updateData()
        self.coeffView.resizeColumnsToContents()
        height = (self.coeffView.horizontalScrollBar().height() +
                  self.coeffView.horizontalHeader().height() +
                  self.coeffView.verticalHeader().sectionSize(0))
        width = 0
        for i in range(self.coeffView.horizontalHeader().count()):
            width+=self.coeffView.columnWidth(i)
        self.coeffView.setMinimumHeight(height)
        self.coeffView.setMinimumWidth(width)

        
def main(calibrationData):
    app = QtWidgets.QApplication([])
    form = CalibrateApp(calibrationData)
    form.show()
    
    app.exec_()
