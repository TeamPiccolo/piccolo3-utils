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

import argparse
from piccolo3.common import piccoloLogging, PiccoloSpectrum, PiccoloSpectraList
import logging
from matplotlib import pyplot

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('picco',metavar='PICCO',nargs='+',help='input piccolo json files')
    parser.add_argument('-d','--debug',action='store_true',default=False,help='enable debug')
    parser.add_argument('--direction',action='append',help='select directions to plot')
    parser.add_argument('--dark',action='store_true',default=False,help='show dark spectra')
    parser.add_argument('--use-original-wavelength-coefficients',action='store_true',default=False,help='use original wavelength coefficients insteat of piccolo coefficients')
    args = parser.parse_args()

    # start logging
    piccoloLogging(debug=args.debug)
    log = logging.getLogger("piccolo.display")

    use_piccolo_coeff = not args.use_original_wavelength_coefficients
    
    if args.direction is None:
        directions = ['upwelling','downwelling']
    else:
        directions = args.direction

    if args.dark:
        spectrum = 'Dark'
    else:
        spectrum = 'Light'

    axes = {}
    fig, a = pyplot.subplots(1,len(directions),sharex=True,sharey=True)
    if len(directions) == 1:
        a = [a]
    for i in range(len(directions)):
        a[i].set_title(directions[i])
        a[i].set_xlabel('wavelength')
        if i == 0:
            a[i].set_ylabel('intensity')
        else:
            a[i].get_yaxis().set_visible(False)
        
        axes[directions[i]] = a[i]
            

    colours = ['red','green','blue','orange','pink']
    instruments = {}
        
    for f in args.picco:
        log.info('reading file %s'%f)

        spectra = PiccoloSpectraList(data=open(f,'r').read())

        if not spectra.haveSpectrum(spectrum):
            log.warning('{} spectrum not available in file {}'.format(spectrum,f))
            continue
        for d in directions:
            for s in spectra.getSpectra(d,spectrum):
                
                if s['SerialNumber'] not in instruments:
                    c = colours[len(instruments)]
                    instruments[s['SerialNumber']] = (c,s['SaturationLevel'])
                w,p = s.getData(piccolo=use_piccolo_coeff)
                if (s.isSaturated):
                    style = '--'
                else:
                    style = '-'
                axes[d].plot(w,p,ls=style,color=instruments[s['SerialNumber']][0])

    handles = []
    labels = []
    haveLabels = False
    for d in directions:
        for s in instruments:
            h = axes[d].axhline(instruments[s][1],color=instruments[s][0])
            if not haveLabels:
                handles.append(h)
                labels.append(s)
        haveLabels = True
    
    fig.legend(handles=handles,loc="lower center",labels=labels,ncol=len(instruments))
    pyplot.subplots_adjust(bottom=0.18)
    pyplot.show()
    
if __name__ == '__main__':
    main()
