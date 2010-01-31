# coding:utf8

import os

is_register_server = False # 是否是注册点机器
sync_internal = 1200 # 同步时间间隔
#web_service_url = "http://localhost/BV_Upload/BVServicePort?wsdl"
#web_service_url = "http://162.105.81.81:7789/Sync2WebServicewsdl"
web_service_url = "http://localhost:7789/Sync2WebServicewsdl"
#web_service_url = "http://162.105.30.159:7789/Sync2WebServicewsdl"
if os.sep == '/':
    data_dir_root = '/d/data/'
else:
    data_dir_root = "D:\\data\\"

mysql_options = {
        'host':'localhost',
        'user':'root',
        'passwd':'root',
        'schema':'bioverify_new',
}

logdir = 'logs'

# 以下部分为程序内部逻辑配置，请勿修改
# 无论注册机还是非注册机都要下载的表
common_download_tables = (
    'card_info',
    'class',
    'result_info',
    'template',
    'person_info',
    'person_extra',
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
    'person_info',
)

tables_with_file = (
    'sample',
    'template',
)

keys = {    
    'card_info':'card_no',
    'result_info':'person_uuid',    
    'person_extra':'person_uuid',
    'person_info':'uuid',
    'class':'uuid',
    'sample':'uuid',
    'template':'uuid',
}

field_exclude = {
    #'person_info':('person_id',), 没有处理这个会有潜在的bug风险
    'card_info':('person_id','person_uuid'),
    'class':('person_id','class_id'),
    'sample':('person_id','class_id', 'sample_id'),
}

import plugin
plugins = {
    'card_info':plugin.CardInfoPlugin,
    'class':plugin.ClassPlugin,
    'sample':plugin.SamplePlugin,
    'template':plugin.TemplatePlugin,
}

