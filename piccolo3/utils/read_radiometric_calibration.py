# Copyright 2018- The Piccolo Team
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

__all__ = ['read_radiometric_calibration']

import numpy
from scipy import interpolate

HEADER = ['description','units','some','start','end','step']
HEADER_TYPE = [str,str,str,float,float,float]

def read_radiometric_calibration(fname):
    indata = open(fname,'r')
    h = indata.readline().split(',')
    caldata = {}
    assert len(HEADER) == len(h)
    for i in range(len(HEADER)):
        caldata[HEADER[i]] = HEADER_TYPE[i](h[i])
    data = []
    for d in indata.readlines():
        data.append(float(d))
    data = numpy.array(data)

    wavelengths = numpy.linspace(caldata['start'],caldata['end'],num=len(data))

    assert (abs(wavelengths[1]-wavelengths[0]-caldata['step']) < 1.e-6)

    caldata['spline'] = interpolate.InterpolatedUnivariateSpline(wavelengths,data)

    return caldata

if __name__ == '__main__':
    import sys

    cal = read_radiometric_calibration(sys.argv[1])

    print(cal)
    

    
