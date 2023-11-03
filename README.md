Helper library and command line tools for dealing with seismic catalogs
and seisan Sfiles.

## Installation

It is recommended to use a virtual environment. You can follow instructions for
[conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
or [venv](https://docs.python.org/3.12/library/venv.html#module-venv).

You can then clone from git:
```bash
git clone https://github.com/khomman/SeisanUtil.git /path/to/seisanutil
```

and install using pip or setup.py:
```bash
cd /path/to/SeisanUtil
pip install .
```
or
```bash
cd /path/to/SeisanUtil
python setup.py install
```

## Usage

Seisan outputs files in [Nordic format](https://seis.geus.net/software/seisan/node243.html#5026).  These
files consist of lines of 80 chars and the last character defines the type of the line. There
are line types for hypocenters, fault plane solutions, phase arrivals, and much more. The purpose of this tool
is to easily read these files and put them into a python environment in order to utilize tools such as
numpy and matplotlib.

### Reading Seisan files

You can read an individual seisan file by using the `read_sfile` function. `read_sfile` will
read the file and return an Event object that contains information about the seismic event.

```
from SeisanUtil.read import read_sfile
ev = read_sfile("/path/to/data/file")
print(ev)
```

An `Event` object contains most of the information contained within the Seisan file. Additionally,
`Event`s contain convenience methods to make plots and calculate parameters associated with the seismic event.
All attributes and methods can be shown by `print ev.__dir__()`.

`Event`s can also be merged into a `Catalog` object. To generate a catalog, provide a list of 
`Event` instances or paths to the datafile.  Once created, a catalog is simply a container
for `Events` and has some basic methods for data processing.

### Ex: Create a travel time plot for several earthquakes
```
from SeisanUtil.catalog import Catalog
from SeisanUtil.event import Event
from SeisanUtil.read import read_sfile

event_1 = read_sfile("tests/Sfiles/01-1544-40L.S201908")
evs = ["tests/Sfiles/01-1300-32L.S202204",
           event_1,
           "tests/Sfiles/04-1905-10L.S202310",
           "tests/Sfiles/13-0031-00L.S201906"]
    cat = Catalog(evs)
    cat.ttime_plot(outfile="TTPlot.png")
```