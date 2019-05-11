# Copyright 2018- The Piccolo Team
#
# This file is part of piccolo3-client.
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

__all__  = ['PiccoloSpectralLines']

from piccolo3.common import PiccoloSpectrum
import numpy

class PiccoloSpectralLines(object):

    def __init__(self, fname):
        """
        load spectral lines from csv file fname
        """
        self._spectraLines = numpy.loadtxt(fname)

    @property
    def lines(self):
        for l in self._spectraLines:
            yield l

    def match(self,peaks,maxDist=2.):
        matched = []
        lines = list(self._spectraLines)
        lines.sort()

        for p,w in peaks:
            for j in range(len(lines)):
                if abs(w-lines[j]) < maxDist:
                    matched.append((p,lines[j]))
                    del lines[j]
                    break
        return matched
