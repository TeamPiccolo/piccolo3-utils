Installation
============
The piccolo3 utilities requre a python3 stack including the qt GUI. Here are some notes on how to install the utilities.
  
Ubuntu
------
On the current LTS version of Ubuntu (20.04) most of the dependencies can be satisfied with system packages:
```
apt install python3 python3-bitarray python3-numpy python3 python3-scipy \
            python3-xarray python3-matplotlib python3-pandas \
            python3-sortedcontainers python3-configobj python3-setuptools \
            python3-pyqt5 pyqt5-dev-tools python3-pyqt-distutils \
            python3-netcdf4
```

I would suggest to install the piccolo3 utilities into a python virtual environment. Assuming you want to keep the virtual environment in `~/piccolo3/venv` run
```
python3 -m venv ~/piccolo3/venv --system-site-packages
```
then activate it and install the missing package
```
. ~/piccolo3/venv/bin/activate
```
Next you need to install [piccolo3-common](https://github.com/TeamPiccolo/piccolo3-common)
```
git clone https://github.com/TeamPiccolo/piccolo3-common.git
cd piccolo3-common
python3 setup.py install
cd ..
```
Now you can install piccolo3-utils
```
git clone https://github.com/TeamPiccolo/piccolo3-utils.git
cd piccolo3-utils
python setup.py build_ui
python setup.py install
python setup.py install_data
```
In future when you want to use the utilities you need to activate the environment. The utilities are in the path.


conda
-----
conda is a crossplatform scientific python distribution. Once you have 
installed miniconda you can create a conda environment using
```
conda env create -f p3utils.yml
```
then activate it 
```
conda activate piccolo3-utils
```
and install the utils
```
python setup.py build_ui
python setup.py install
python setup.py install_data
```
