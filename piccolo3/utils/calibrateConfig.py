# Copyright 2018 The Piccolo Team
#
# This file is part of piccolo2-utils.
#
# piccolo2-utils is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# piccolo2-server is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with piccolo2-server.  If not, see <http://www.gnu.org/licenses/>.

"""
.. moduleauthor:: Magnus Hagdorn <magnus.hagdorn@ed.ac.uk>

"""

__all__ = ['CalibrateConfig']

import os.path
import sys
from glob import glob
import logging
from configobj import ConfigObj, flatten_errors
from validate import Validator
from pprint import pprint as pretty # To pretty-print output when testing.

# the defaults
defaultCfgStr = """
# This is the calibration configuration file.

[calibrate]
  [[__many__]]
    # CSV file containing spectral lines to be matched
    spectral_lines = string(min=1) 
    # spectra files to load
    spectra = string_list(min=1)
"""

# populate the default  config object which is used as a validator
calibrateDefaults = ConfigObj(defaultCfgStr.split('\n'),list_values=False,_inspec=True)
validator = Validator()

class CalibrateConfig(object):
    """object managing the calibration config file"""

    def __init__(self):
        self._cfg = ConfigObj(configspec=calibrateDefaults)
        self._cfg.validate(validator)

    def readCfg(self,fname):
        """read and parse configuration file"""

        if not os.path.isfile(fname):
            msg = 'no such configuration file {0}'.format(fname)
            logging.error(msg)
            raise RuntimeError(msg)


        self._cfg.filename = fname
        self._cfg.reload()
        if not self._cfg.validate(validator):
            print (self._cfg.validate(validator,preserve_errors=True))
            msg = 'Could not read config file {0}'.format(fname)
            logging.error(msg)
            raise RuntimeError(msg)

        # resolve file names
        dname = os.path.dirname(fname)
        sname = os.path.join(os.path.dirname(sys.argv[0]),'..','share','piccolo2-util')
        for c in self.cfg['calibrate']:
            name = self.cfg['calibrate'][c]['spectral_lines']
            # first look in the PWD, then relative to the config file, then in the system directory
            for p in ['',dname,sname]:
                fname = os.path.abspath(os.path.join(p,name))
                if os.path.exists(fname):
                    break
            else:
                msg = 'Could not find spectral lines %s'%name
                logging.error(msg)
                raise RuntimeError(msg)
            self.cfg['calibrate'][c]['spectral_lines'] = fname

            sFiles = []
            for s in self.cfg['calibrate'][c]['spectra']:
                # first look in the PWD, then relative to the config file
                for p in ['',dname]:
                    gs =  glob(os.path.abspath(os.path.join(p,s)))
                    if len(gs)>0:
                        break
                else:
                    msg = 'no such file(s) %s'%s
                    logging.error(msg)
                    raise RuntimeError(msg)
                sFiles += gs
            self.cfg['calibrate'][c]['spectra'] = sFiles
            
    @property
    def cfg(self):
        return self._cfg
    
if __name__ == '__main__':
    import sys

    cfg = CalibrateConfig()

    if len(sys.argv)>1:
        cfg.readCfg(sys.argv[1])

    print (pretty(cfg.cfg.dict()))
