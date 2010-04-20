#!/usr/bin/env python

import socket
#import fcntl
import struct
import re
from subprocess import Popen, PIPE

def get_ip_address():
    return re.search('\d+\.\d+\.\d+\.\d+',Popen('ipconfig', stdout=PIPE).stdout.read()).group(0)