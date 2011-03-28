
try:
    from version import __version__
except ImportError:
    __version__ = 'unknown (package not built using setuptools)'

import circuit
import datasource
import plot
import plugins
import pywave
import signaltype
import xh_searchctrl
