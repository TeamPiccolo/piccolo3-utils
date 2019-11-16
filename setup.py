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

from setuptools import setup, find_packages
from pyqt_distutils.build_ui import build_ui
import setuptools.command.build_py

class BuildPyCommand(setuptools.command.build_py.build_py):
  """Custom build command."""

  def run(self):
    self.run_command('build_ui')
    setuptools.command.build_py.build_py.run(self)

cmdclass = {'build_ui': build_ui,
            'build_py': BuildPyCommand,}
    
setup(
  name = "piccolo3-utils",
  namespace_packages = ['piccolo3'],
  packages = find_packages(),
  use_scm_version=True,
  setup_requires=['setuptools_scm'],
  install_requires = ['bitarray',
                      'numpy',
                      'scipy>1.2.0',
                      'piccolo3-common',
                      'xarray',
                      'matplotlib',
                      'pandas',
                      'sortedcontainers',
                      'configobj',
  ],
  data_files=[
    ('share/piccolo3-util',["data/HgArLines.csv",]),
  ],
  entry_points={
    'console_scripts': [
      'piccolo3-read = piccolo3.readpicco:main',
      'piccolo3-calibrate = piccolo3.radiometric_cal:main',
      'piccolo3-wavelengthCalibration = piccolo3.pcalibrate:main',
      'piccolo3-display = piccolo3.disppicco:main',
    ],
    'gui_scripts': [
      'piccolo3-wavelengthCalibration-gui = piccolo3.pcalibrateg:main',
    ],
  },
  cmdclass=cmdclass,
  # metadata for upload to PyPI
  author = "Magnus Hagdorn, Alasdair MacArthur, Iain Robinson",
  description = "Part of the piccolo3 system. This package provides utility modules",
  license = "GPL",
  url = "https://bitbucket.org/uoepiccolo/piccolo3-utils",
)
