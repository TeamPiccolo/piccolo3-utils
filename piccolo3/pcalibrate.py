from piccolo3.utils import CalibrateData, CalibrateConfig
import argparse
import sys, os.path
from matplotlib import pyplot
import numpy
import pandas

markers = "ov^<>spP*Dd"

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
            spectralLinesName=os.path.join(os.path.dirname(sys.argv[0]),'..','share','piccolo2-util','HgArLines.csv')
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

    print ('original',calibrationData.origCoeff)
    print ('new', calibrationData.newCoeff)

    # plot data
    f,ax = pyplot.subplots(2,2, sharex=True)
    spectralLinesColour = {}
    spectralLinesMarker = {}
    i = 0
    for l in calibrationData.spectralLines:
        spectralLinesColour[l] = 'C%d'%(i%10)
        spectralLinesMarker[l] = markers[i%len(markers)]
        i = i+1

    for s in calibrationData.spectralLines:
        for l in calibrationData.spectralLines[s].lines:
            for j in range(2):
                ax[0,j].axvline(l,color=spectralLinesColour[s])
        matched = calibrationData.peaks[(calibrationData.peaks.lightSource==s) & (calibrationData.peaks.wavelength>0)]
        w = calibrationData.origWavelength(matched.index.values)
        ax[1,0].plot(w,matched.wavelength.values-w,'o',color=spectralLinesColour[s])
        w = calibrationData.newWavelength(matched.index.values)
        ax[1,1].plot(w,matched.wavelength.values-w,'o',color=spectralLinesColour[s])

    for i in range(calibrationData.numSpectra):
        c = 'C%d'%(i%10)
        s = calibrationData.spectra[calibrationData.spectra.fileID==i]
        ax[0,0].plot(s.orig_wavelength.values,s.intensity.values,color=c)
        ax[0,1].plot(s.new_wavelength.values,s.intensity.values,color=c)

    for j in range(2):
        ax[j,0].set_xlim(s.orig_wavelength.values[[0,-1]])
        ax[j,1].set_xlim(s.new_wavelength.values[[0,-1]])

    
    pyplot.suptitle('%s %s'%(calibrationData.serialNumber,calibrationData.direction),fontsize=16)
    ax[0,0].set_title('original')
    ax[0,1].set_title('new')
    ax[1,0].set_ylabel('mismatch at peaks')
    ax[0,0].set_ylabel('counts')
    ax[1,0].set_xlabel('wavelength')
    ax[1,1].set_xlabel('wavelength')
        
    pyplot.show()
