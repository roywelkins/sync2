#!/usr/bin/env python

from distutils.core import setup
import py2exe

opts = {
    "py2exe": {
        "compressed": 1,
        "optimize": 2,
        "bundle_files": 1,
        "dll_excludes": ['POWRPROF.dll', 'w9xpopen.exe'],
        "excludes": ['conf.py'],
    }
}

datafiles = [
    ('', ['setup.bat', 'uninstall.bat', 'conf.py'])
]

setup(service=["sync2service"], options=opts, zipfile="sync2.lib", data_files=datafiles)
#setup(console=['sync2.py'], options=opts, zipfile="sync2.lib", data_files=datafiles)
#setup(console=['sync2service.py'])