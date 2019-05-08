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


__all__ = ['PiccoloProcessedData','read_picco']

from piccolo3.common import PiccoloSpectrum, PiccoloSpectraList
import datetime, pytz
import xarray
import numpy
import logging

class PiccoloProcessedData:
    def __init__(self):
        self._serial = None
        self._direction = None
        self._wavelengths = None

        self._runs = []
        self._batches = []
        self._sequences = []
        self._data = []

        self._timestamp = []
        self._temperature_target = []
        self._temperature = []

    @property
    def serial(self):
        return self._serial
    @property
    def direction(self):
        return self._direction

    @property
    def data(self):
        data = xarray.Dataset({'temperature': (['measurement'], self._temperature),
                               'temperature_target': (['measurement'], self._temperature_target),
                               'time' :  (['measurement'], self._timestamp),
                               'data': (['measurement','wavelengths'], self._data),
                               },
                              coords = {'runs': (['measurement'], self._runs),
                                        'batches': (['measurement'], self._batches),
                                        'sequences': (['measurement'], self._sequences),
                                        'wavelengths': self._wavelengths,
                              } )
        data.attrs['serial'] = self.serial
        data.attrs['direction'] = self.direction
        return data
    
    def add(self, spec, data=None):
        assert isinstance(spec,PiccoloSpectrum)
        if self._serial is None:
            self._serial = spec['SerialNumber']
            self._direction = spec['Direction']
            self._wavelengths = numpy.array(spec.waveLengths)
        assert self.serial == spec['SerialNumber']
        assert self.direction == spec['Direction']

        self._runs.append(spec['Run'])
        self._batches.append(spec['Batch'])
        self._sequences.append(spec['SequenceNumber'])
        if data is not None:
            self._data.append(data)
        else:
            self._data.append(spec.pixels)
        self._timestamp.append(datetime.datetime.strptime(spec['Datetime'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.utc))
        if 'TemperatureDetectorActual' in spec.keys():
            self._temperature_target.append(spec['TemperatureDetectorSet'])
            self._temperature.append(spec['TemperatureDetectorActual'])
        else:
            self._temperature_target.append(None)
            self._temperature.append(None)

def read_picco(infiles):
    log = logging.getLogger("piccolo.read")

    dark = {}
    data_sets = {}
    
    for f in infiles:
        log.info('reading file %s'%f)

        spectra = PiccoloSpectraList(data=open(f,'r').read())

        for s in spectra:
            if s['SerialNumber'] not in data_sets:
                data_sets[s['SerialNumber']] = {}
            if s['Direction'] not in data_sets[s['SerialNumber']]:
                data_sets[s['SerialNumber']][s['Direction']] = PiccoloProcessedData()
            
            if s['SerialNumber'] not in dark:
                dark[s['SerialNumber']] = {}
            if s['Direction'] not in dark[s['SerialNumber']]:
                dark[s['SerialNumber']][s['Direction']] = None
            if s['Dark']:
                dark[s['SerialNumber']][s['Direction']] = s
            else:
                d = dark[s['SerialNumber']][s['Direction']]
                assert (abs(s['IntegrationTime']-d['IntegrationTime'])<1.)
                # apply total dark correction
                pixels = (s.corrected_pixels - d.corrected_pixels)/s['IntegrationTime']
                data_sets[s['SerialNumber']][s['Direction']].add(s,data=pixels)

    return data_sets