import os

if os.sep=='/':
    data_dir_root = '/d/data_server/'
else:
    data_dir_root = "D:\\data_server\\"

mysql_options = {
        'host':'localhost',
        'user':'root',
        'passwd':'root',
        'schema':'bioverify',
}
