# Copyright 2018 The Piccolo Team
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

"""
.. moduleauthor:: Magnus Hagdorn <magnus.hagdorn@ed.ac.uk>

"""

__all__ = ['CalibrateData']

import numpy, pandas
from sortedcontainers import SortedSet
from .matchSpectralLines import PiccoloSpectralLines
from piccolo3.common import PiccoloSpectraList
from scipy.signal import find_peaks

def gaussian(a,b,c,x):
    return a*numpy.exp(-(x-b)**2/(2*c**2))

class CalibrateData(object):
    """main data structure holding calibration data"""

    def __init__(self,serialNumber, direction):
        """
        Parameters
        ----------
        serialNumber: the serial number of the spectrometer
        direction: the direction
        """

        self._serialNumber = serialNumber
        self._direction = direction

        self._spectralLines = {}

        self._piccoFiles = []
        self._spectra = pandas.DataFrame(columns = ['pixel','intensity','orig_wavelength','fileID','lightSource','new_wavelength'])
        
        self._peaks = pandas.DataFrame(columns = ['pixel','lightSource','wavelength']).set_index('pixel')

        self._origCoeffs = None
        self._origPoly = None
        self._newCoeffs = None
        self._newPoly = None

        self._saturation = None
        self._minIntensity = None
        self._maxIntensity = None
        
    @property
    def serialNumber(self):
        """serial number of spectrometer"""
        return self._serialNumber
    @property
    def direction(self):
        """measurement direction"""
        return self._direction
    @property
    def spectralLines(self):
        """dictionary holiding spectral lines for each light source"""
        return self._spectralLines
    @property
    def lightsources(self):
        """sorted list of light source names (the keys to spectralLines)"""
        ls = list(self.spectralLines.keys())
        ls.sort()
        return ls
    @property
    def spectra(self):
        """pandas dataframe containing all spectra"""
        return self._spectra
    @property
    def numSpectra(self):
        """the number of spectra"""
        return len(self._piccoFiles)
    @property
    def minIntensity(self):
        """the minimum intensity considered for finding peaks"""
        if self._minIntensity is None:
            return 5000
        else:
            return self._minIntensity
    @minIntensity.setter
    def minIntensity(self,arg):
        a = int(arg)
        assert a>0
        if self.maxIntensity is not None:
            assert a<self.maxIntensity
        self._minIntensity = a
    @property
    def maxIntensity(self):
        """the maximum intensity considered for finding peaks"""
        return self._maxIntensity
    @maxIntensity.setter
    def maxIntensity(self,arg):
        a = int(arg)
        if self.minIntensity is not None:
            assert a>self.minIntensity
        if self._saturation is not None:
            assert a<self._saturation
        self._maxIntensity = a
    @property
    def saturationPercentage(self):
        """the maxium intensity as a percentage of the saturation"""
        if self.maxIntensity is None or self._saturation is None:
            return None
        else:
            return 100*float(self.maxIntensity)/float(self._saturation)
    @saturationPercentage.setter
    def saturationPercentage(self,arg):
        if self._saturation is not None:
            self.maxIntensity = int(0.01*arg*self._saturation)
    @property
    def peakHeight(self):
        """height used for finding peaks"""
        if self.maxIntensity is not None:
            return [self.minIntensity,self.maxIntensity]
        else:
            return self.maxIntensity
    @property
    def peaks(self):
        """a pandas dataframe containing the peaks and associated wavelength for each light source"""
        return self._peaks
    @property
    def origCoeff(self):
        """the original wavelenth coefficients"""
        return self._origCoeffs
    @origCoeff.setter
    def origCoeff(self,coeffs):
        coeffs = numpy.array(coeffs)
        if self._origCoeffs is None:
            self._origCoeffs = coeffs
        else:
            if numpy.any(numpy.abs(self._origCoeffs-coeffs)>1e-5):
                raise RuntimeError('trying to change original wavelength coefficients')
    @property
    def origPoly(self):
        """polynomial object using original wavelength coefficients"""
        if self._origPoly is None:
            if self.origCoeff is None:
                raise RuntimeError("original wavelength coefficients not set yet")
            self._origPoly = numpy.poly1d(self.origCoeff)
        return self._origPoly    
    def origWavelength(self,arg):
        """compute wavelength using the original wavelength coefficients
        Parameters
        ----------
        arg - a single pixel number or a list/array of pixel numbers
        """
        return self.origPoly(arg)
    @property
    def newCoeff(self):
        """the new wavelenth coefficients"""
        return self._newCoeffs
    @newCoeff.setter
    def newCoeff(self,coeffs):
        c = numpy.array(coeffs,dtype=float)
        if self._newCoeffs is None or len(c)!=len(self._newCoeffs) or numpy.all(numpy.abs(c-self._newCoeffs)>1e-14):
            self._newCoeffs = c
            self._newPoly  = None
            self.updateNewWavelength()
    @property
    def newPoly(self):
        """polynomial object using new wavelength coefficients"""
        if self._newPoly is None:
            if self.newCoeff is None:
                raise RuntimeError("new wavelength coefficients not set yet")
            self._newPoly = numpy.poly1d(self.newCoeff)
        return self._newPoly
    
    def newWavelength(self,arg):
        """compute wavelength using the new wavelength coefficients
        Parameters
        ----------
        arg - a single pixel number or a list/array of pixel numbers
        """
        return self.newPoly(arg)

    def addLightSource(self,name,spectralLines):
        """
        add a new light source

        Parameters
        ----------
        name - the name of the light source
        spectralLines - name of the file containing the spectral lines
        """
        if name in self.spectralLines:
            raise RuntimeError('light source %s is already loaded'%name)
        self.spectralLines[name] = PiccoloSpectralLines(spectralLines)
        

    def addSpectrum(self,lightSource,piccoFile):
        """
        add a spectrum

        Parameters
        ----------
        lightSource - the name of the light source used to collect the spectra
        piccoFile - the name of the piccolo file to be loaded
        """

        if lightSource not in self.spectralLines:
            raise RuntimeError('light source %s not registered'%lightSource)
        
        with open(piccoFile,'r') as inFile:
            spectra = PiccoloSpectraList(data=inFile.read())

            # loop over spectra
            for s in spectra:
                sn = s['SerialNumber']
                dr = s['Direction']
                if sn != self.serialNumber or dr != self.direction:
                    # not the data we are looking for
                    continue


                self.origCoeff = s['WavelengthCalibrationCoefficients'][::-1]
                if self._saturation is None:
                    self._saturation = s['SaturationLevel']
                if self.saturationPercentage is None:
                    # use 80% of saturation
                    self.saturationPercentage = 80

                fileID = self.numSpectra
                nPixels = s.getNumberOfPixels()
                
                data = {'pixel' : numpy.arange(nPixels),
                        'intensity' : s.pixels,
                        'fileID' : [fileID]*nPixels,
                        'lightSource' : [lightSource]*nPixels
                        }
                data['orig_wavelength'] = self.origWavelength(data['pixel'])
                data = pandas.DataFrame(data)
                self._spectra = self._spectra.append(data,ignore_index=True)

                # find the peaks
                peaks,_ = find_peaks(s.pixels,height= self.peakHeight)
                for p in peaks:
                    self.peaks.loc[p] = {'lightSource':lightSource,'wavelength':-1}
                self._peaks = self._peaks.sort_index()

                # all good, add processed file to list of files
                self._piccoFiles.append(piccoFile)
    
    def matchWavelength(self):
        for l in self.spectralLines:
            peaks = self.peaks[self.peaks==l].index.values
            p = zip(peaks,self.origWavelength(peaks))
            for p,w in self.spectralLines[l].match(p):
                self.peaks.loc[p].wavelength = w

    def fitWavelength(self,order=3,optimseWavelength=None,gaussianWidth=100):
        p = self.peaks[self.peaks.wavelength>0]
        if optimseWavelength is not None:
            weights = 0.5+gaussian(0.5,optimseWavelength,gaussianWidth,p.index.values)
        else:
            weights = None
        self.newCoeff = numpy.polyfit(p.index.values,p.wavelength.values,order,w=weights)
                
    def updateNewWavelength(self):
        self.spectra.new_wavelength[:] = self.newWavelength(self.spectra.pixel.values)
