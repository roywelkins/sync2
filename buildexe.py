#!/usr/bin/env python

from distutils.core import setup
import py2exe

opts = {
    "py2exe": {
        "compressed": 1,
        "optimize": 2,
        "bundle_files": 1,
        "dll_excludes": ['POWRPROF.dll', 'w9xpopen.exe'],
        "packages": ['lxml', 'soaplib', 'gzip', 'pytz', 'servicemanager', 'xml', 'MySQLdb'],
        "dist_dir": 'dist_client',
    }
}

datafiles = [
    ('', ['sync2.cmd',
          'conf.xml',
          ])
]

datafiles_server = [
    ('', ['serverconf.xml',])
]

opts_server = {
    "py2exe": {
        "compressed": 1,
        "optimize": 2,
        "bundle_files": 1,
        "dll_excludes": ['POWRPROF.dll', 'w9xpopen.exe'],
        #"excludes": ['conf', 'serverconf'],
        "packages": ['lxml', 'soaplib', 'gzip', 'pytz', 'servicemanager', 'xml'],
        'dist_dir':'dist_server',
    }
}

#setup(console=['sync2.py'], options=opts, zipfile="sync2.lib", data_files=datafiles)
#setup(console=['sync2webservice.py'], options=opts_server, zipfile="sync2webservice.lib", data_files=datafiles_server)

setup(console=['upload_card_info.py'], options=opts, zipfile="sync2.lib", data_files=datafiles)
