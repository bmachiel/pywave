#!/bin/env python

from setuptools import setup
from subprocess import Popen, PIPE

# write the git version to pywave/version.py
# based on version.py by Douglas Creager <dcreager@dcreager.net>
# http://dcreager.net/2010/02/10/setuptools-git-version-numbers/
try:
    p = Popen(['git', 'describe', '--abbrev=4'],
              stdout=PIPE, stderr=PIPE)
    p.stderr.close()
    line = p.stdout.readlines()[0]
    version = line.strip()[1:]
except:
    print("A problem occured while trying to run git. "
          "Version information is unavailable!")
    version = 'unknown'

version_file = open('pywave/version.py', 'w')
version_file.write("__version__ = '%s'\n" % version)
version_file.close()


setup(
    name='pywave',
    version=version,
    packages=['pywave', 'pywave.plugins'],
    scripts=['scripts/pywave'],
    package_dir={'pywave': 'pywave'},
    package_data={'pywave': ['pywave.xrc', 'images/*.png']},
    requires=['wx', 'enthought.enable', 'enthought.chaco', 'numpy', 'nport'],
    provides=['pywave'],
    #test_suite='nose.collector',
    
    author="Brecht Machiels",
    author_email="brecht.machiels@esat.kuleuven.be",
    description="A modular waveform viewer",
    license="GPL",
    keywords="HSPICE touchstone citi",
    url="https://github.com/bmachiel/pywave",
)
