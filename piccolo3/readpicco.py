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
from piccolo3.utils import read_picco
import logging


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('picco',metavar='PICCO',nargs='+',help='input piccolo json files')
    parser.add_argument('-c','--calibration-files',default=[],nargs='*',help='radiometric calibration files, you can use this option multiple time and/or use wildcards')
    parser.add_argument('-p','--prefix',default='',help='output prefix')
    parser.add_argument('-d','--debug',action='store_true',default=False,help='enable debug')
    args = parser.parse_args()

    # start logging
    piccoloLogging(debug=args.debug)

    infiles = args.picco
    infiles.sort()
    data = read_picco(infiles,calibration=args.calibration_files)

    for s in data.keys():
        for c in data[s].keys():
            outname = args.prefix+'%s_%s.nc'%(s,c)
            data[s][c].data.to_netcdf(outname)
    
if __name__ == '__main__':
    main()
