# coding:utf8

import os

is_register_server = False # 是否是注册点机器
sync_internal = 1200 # 同步时间间隔
#web_service_url = "http://localhost/BV_Upload/BVServicePort?wsdl"
web_service_url = "http://localhost:7789/Sync2WebServicewsdl"
if os.sep == '/':
    data_dir_root = '/d/data/'
else:
    data_dir_root = "D:\\data\\"

mysql_options = {
        'host':'localhost',
        'user':'root',
        'passwd':'root',
        'schema':'bioverify',
}

logdir = 'logs'

# 以下部分为程序内部逻辑配置，请勿修改
# 无论注册机还是非注册机都要下载的表
common_download_tables = (
    'card_info',
    'class',
    'result',
    'template',
    'student_info',
    'student_info_extra',
)
# 无论注册机还是非注册机都要上传的表
common_upload_tables = (
    'sample',
    'record',
)

server_download_tables = (   
)

server_upload_tables = (
    'card_info',
    'class',
    'template',
    'student_info',
    'student_info_extra',
)

tables_with_file = (
    'sample',
    'template',
)

keys = {    
    'card_info':'card_no',
    'result':'student_id',
    'student_info':'student_id',
    'student_info_extra':'student_id',
    'class':'uuid',
    'sample':'uuid',
    'template':'uuid',
}
