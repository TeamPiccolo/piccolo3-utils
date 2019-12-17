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
import numpy

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('picco',metavar='PICCO',nargs='+',help='input piccolo json files')
    parser.add_argument('-d','--debug',action='store_true',default=False,help='enable debug')

    args = parser.parse_args()

    # start logging
    piccoloLogging(debug=args.debug)
    log = logging.getLogger("piccolo.display")

    if len(args.picco) > 1:
    
        data = {}

        for f in args.picco:
            log.debug('reading file %s'%f)

            spectra = PiccoloSpectraList(data=open(f,'r').read())

            for s in spectra:
                normalised_dark = s.dark_pixels/s['IntegrationTime']

                if s['SerialNumber'] not in data:
                    data[s['SerialNumber']] = {'mean':[],
                                            'std':[]}
                data[s['SerialNumber']]['mean'].append(numpy.mean(normalised_dark))
                data[s['SerialNumber']]['std'].append(numpy.std(normalised_dark))

        for s in data:
            x = numpy.arange(len(data[s]['mean']))
            pyplot.errorbar(x,data[s]['mean'],yerr=data[s]['std'],fmt='o',label=s)
    else:
        spectra = PiccoloSpectraList(data=open(args.picco[0],'r').read())

        for s in spectra:
            normalised_dark = s.dark_pixels/s['IntegrationTime']
            p=pyplot.plot(normalised_dark,'o',label='{} {}'.format(s['SerialNumber'],s['Direction']))
            pyplot.axhline(normalised_dark.mean(),color=p[0].get_color())
        

    pyplot.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
                  ncol=2, mode="expand", borderaxespad=0.)
    pyplot.show()
        
if __name__ == '__main__':
    main()
