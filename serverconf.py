from xml.etree import ElementTree
from xml.etree.ElementTree import Element

root = ElementTree.parse('serverconf.xml').getroot()

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

from baseconf import serverplugins