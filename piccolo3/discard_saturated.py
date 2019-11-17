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
from piccolo3.common import piccoloLogging, PiccoloSpectraList
import logging
from pathlib import Path
import os, shutil

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input',metavar='INPUT',help='name of the input directory')
    parser.add_argument('output',metavar='OUTPUT',help='name of the output directory')
    parser.add_argument('-d','--debug',action='store_true',default=False,help='enable debug')

    args = parser.parse_args()

    # start logging
    piccoloLogging(debug=args.debug)
    log = logging.getLogger("piccolo.discard_saturated")

    inpath = Path(args.input)
    outpath = Path(args.output)

    if not outpath.exists():
        os.mkdir(outpath)
    
    for f in inpath.rglob('*.pico'):
        log.debug('reading file %s'%f)
        try:
            spectra = PiccoloSpectraList(data=open(f,'r').read())
        except:
            log.error('cannot read file %s'%f)
            continue

        if spectra.isSaturated:
            prefix = 'saturated'
        else:
            prefix = 'not-saturated'
        o = outpath.joinpath(prefix,f.relative_to(inpath))

        if not o.parent.exists():
            os.makedirs(o.parent)

        shutil.copy2(f,o)
            

    
if __name__ == '__main__':
    main()
