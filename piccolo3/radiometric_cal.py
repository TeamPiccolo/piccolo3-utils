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
from piccolo3.common import piccoloLogging
from piccolo3.utils import read_radiometric_calibration
import xarray

from matplotlib import pyplot

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dn',help='name of input dn file')
    parser.add_argument('calibration',help='name of input calibration file')
    parser.add_argument('-c','--store-csv',action='store_true',default=False,
                        help="store as csv file")
    parser.add_argument('output',help='name of output calibration file')
    parser.add_argument('-d','--debug',action='store_true',default=False,help='enable debug')
    args = parser.parse_args()

    dn = xarray.open_dataset(args.dn)
    cal = read_radiometric_calibration(args.calibration)

    # only use good pixels
    spectra = dn.spectra.where(dn.spectra>1)
    
    mean_spectrum = spectra.mean(dim='measurement')
    target = cal['spline'](dn.wavelengths)
    coeff = target/mean_spectrum

    calibration = xarray.Dataset({'mean_spectrum' : (['wavelengths'], mean_spectrum),
                                  'calibration_coeff' : (['wavelengths'],coeff)},
                                 coords = {'wavelengths' : dn.wavelengths})


    for k in ['serial','direction']:
        calibration.attrs[k] = dn.attrs[k]

    if args.store_csv:
        calibration.to_dataframe().to_csv(args.output)
    else:
        calibration.to_netcdf(args.output)
    
    if False:
        f, (ax1, ax2, ax3) = pyplot.subplots(3, 1, sharex=True)
        ax1.plot(dn.wavelengths,mean_spectrum)
        ax1.set_ylabel('corrected and normalised dn')
        ax2.plot(dn.wavelengths,target)
        ax2.set_ylabel('radiometric')
        ax3.plot(dn.wavelengths,coeff)
        ax3.set_xlabel('wavelength')
        ax3.set_ylabel('calibration coefficients')
    
        pyplot.show()

if __name__ == '__main__':
    main()
