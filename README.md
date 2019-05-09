Utilities for Processing Piccolo Data
=====================================

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