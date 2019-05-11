#!/usr/bin/env python

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

import piccolo3.utils.CalibrateApp 
from piccolo3.utils import CalibrateData, CalibrateConfig
import argparse
import sys, os.path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('spectra',nargs='*',help='the spectra files to load')
    parser.add_argument('-c','--config',help="read config file")
    parser.add_argument('-l','--spectral-lines',help="csv file containing spectral lines")
    parser.add_argument('--min',type=float,default=5000.,help='minimum delta for peak, default 5000.')
    parser.add_argument('-s','--saturation-percentage',type=float,default=90.,help='percentage of saturation level above which peaks are ignored')
    parser.add_argument('-d','--direction',help="select the direction to process, default: process all directions")
    parser.add_argument('-n','--serial-number',help="select the spectrometer to process, default: process all spectrometers")
    parser.add_argument('-w','--wavelength',type=float,help="optimise for wavelength by applying a Gaussian weight centred at wavelength")
    parser.add_argument('-g','--gaussian-width',type=float,default=100.,help='width of gaussian in nm, default=100.')
    parser.add_argument('--shift',action='store_true',default=False,help='shift wavelengths to match center wavelength used for Gaussian weight')
    parser.add_argument('-v','--version',action='store_true',default=False,help="print version and exit")
    
    args = parser.parse_args()

    if args.version:
        from utils import __version__
        print (__version__)
        sys.exit(0)

    if args.config is not None:
        cfg = CalibrateConfig()
        cfg.readCfg(args.config)
        calibrate = cfg.cfg['calibrate']
    else:
        if args.spectral_lines is not None:
            spectralLinesName = args.spectral_lines
        else:
            spectralLinesName=os.path.join(os.path.dirname(sys.argv[0]),'..','share','piccolo3-util','HgArLines.csv')
        if not os.path.isfile(spectralLinesName):
            parser.error('could not find file containing spectra lines')
            sys.exit(1)       
            
        calibrate = {}
        c = os.path.basename(spectralLinesName)
        calibrate[c] = {}
        calibrate[c]['spectral_lines'] = spectralLinesName
        calibrate[c]['spectra'] = args.spectra
        

    calibrationData = CalibrateData(args.serial_number,args.direction)
    calibrationData.minIntensity = args.min
    calibrationData.saturationPercentage = args.saturation_percentage
    for c in calibrate:
        calibrationData.addLightSource(c,calibrate[c]['spectral_lines'])
        for sf in calibrate[c]['spectra']:
            calibrationData.addSpectrum(c,sf)
            
    if calibrationData.numSpectra == 0:
        print ('no data')
        sys.exit(1)

    # match and optimise wavelengths
    calibrationData.matchWavelength()
    calibrationData.fitWavelength()
    
    piccolo3.utils.CalibrateApp.main(calibrationData)

if __name__ == '__main__':
    main()
