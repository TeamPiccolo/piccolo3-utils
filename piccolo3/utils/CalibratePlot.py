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

__all__ = ['CalibratePlot']

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import time
from PyQt5 import QtCore
import numpy

class CalibratePlot(FigureCanvas):
    BASE_SCALE = 1.5
    BASE_DELTA = 0.0001
    def __init__(self,parent=None):
        super(CalibratePlot,self).__init__(Figure())
        self.setParent(parent)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.misfitCallback = None

        self.canvas.mpl_connect('pick_event', self.onpick)

        self.data = None
        self._theplot = None

        self.draw()
        
    @property
    def theplot(self):
        if self._theplot == None:
            #self.figure.subplots_adjust(hspace=0.4, wspace=0.4)
            self._theplot =[]
            self._theplot.append(self.figure.add_subplot(2,1,1))
            self._theplot.append(self.figure.add_subplot(2,1,2,sharex=self._theplot[0]))
        return self._theplot

    def setCallback(self,callback):
        self.misfitCallback = callback
    
    def onpick(self,event):
        this = event.artist
        idx = event.ind
        w = this.get_xdata()[idx][0]
        if self.misfitCallback is not None:
            self.misfitCallback(w)
        else:
            print (w)
    
    def plotData(self,lightsource):

        for i in range(2):
            self.theplot[i].clear()
        
        for l in self.data.spectralLines[lightsource].lines:
            self.theplot[0].axvline(l,color='k')
                
        spectra = self.data.spectra[self.data.spectra.lightSource==lightsource]
        fileIDs = numpy.unique(spectra.fileID.values)
        fileIDs.sort()
        for fid in fileIDs:
            c = 'C%d'%(fid%10)
            s = spectra[spectra.fileID==fid]

            self.theplot[0].plot(s.new_wavelength.values,s.intensity.values,color=c)

        self.theplot[0].set_xlim(s.new_wavelength.values[0],s.new_wavelength.values[-1])

        matched = self.data.peaks[(self.data.peaks.lightSource==lightsource) & (self.data.peaks.wavelength>0)]
        w = self.data.newWavelength(matched.index.values)
        self.theplot[1].plot(w,matched.wavelength.values-w,'ob',picker=5)
        
        self.draw()
