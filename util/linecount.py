#!/usr/bin/env python

import os
import sys

os.chdir('..')
filenames = os.listdir('.')
c=0
for name in filenames:
    suffix = name[name.rfind('.'):]
    if suffix=='.py':
        f = open(name)
        c+=len(f.readlines())
print c