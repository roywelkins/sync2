# coding:utf8

from xml.etree import ElementTree
from xml.etree.ElementTree import Element

root = ElementTree.parse('conf.xml').getroot()

is_register_server = root.find('is_register_server').text
if is_register_server=='False':
    is_register_server = False
else:
    is_register_server = True

sync_internal = root.find('sync_internal').text
web_service_url = root.find('web_service_url').text
import os
if os.pathsep=='\\':
    data_dir_root = root.find('data_dir_root_linux').text
else:
    data_dir_root = root.find('data_dir_root_windows').text

m = root.find('mysql_options')
mysql_options = {}
mysql_options['host'] = m.find('host').text
mysql_options['user'] = m.find('user').text
mysql_options['passwd'] = m.find('passwd').text
mysql_options['schema'] = m.find('schema').text

logdir = root.find('logdir').text

from baseconf import *