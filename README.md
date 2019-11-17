Utilities for Processing Piccolo Data
=====================================

Some useful utilities for the piccolo system.

wavelengthCalibration
---------------------
Program used to calibrate the wavelengths by matching spectral lines. If you use a single light source, ie a single set of spectral lines you can specify a file containing the spectral lines and the spectra to fit on the command line. Otherwise you have to use a config file, with the following content

```
[calibrate]
[[some_name_a]]
spectral_lines = name_spectral_line_file
spectra = spectra_1, spectra_s, # you need to have at least one comman as it is a list of files

[[some_name_b]]
spectral_lines = another_spectral_line_file
spectra = spectra_3*, #you can also use globs
```

piccolo3-display
----------------
Display all spectra in a series of piccolo JSON files

piccolo3-discard-saturated
--------------------------
Read a directory tree containing piccolo files and sort them into saturated and not-saturated directories maintaing the same directory structure.

piccolo3-read
-------------
Read a set of raw piccolo json files, apply corrections and store in xarray dataset. The following corrections will be applied:
* non-linearity correction
* dark current correction
* the data are normalised by integration time
The program will apply radiometric calibration files if supplied.

piccolo3-calibrate
------------------
Produce radiometric calibration files.

Using xarray datasets
---------------------
```python
# load basic modules
import xarray
import numpy
# and for plotting
from matplotlib import pyplot

# load a dataset
data = xarray.open_dataset('all_QEP00114_Upwelling.nc')

# plot all spectra
# note, the data needs to be transposed
pyplot.plot(data.wavelengths, data.spectra.T)
pyplot.show()

# select data for a particular run and batch
d = data.where(numpy.logical_and(data.runs == 'ES_TrialPlot10', data.batches == 0))
# and plot mean of all sequences
pyplot.plot(d.wavelengths,d.spectra.mean(dim='measurement'))
pyplot.show()

```