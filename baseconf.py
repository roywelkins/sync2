#!/usr/bin/env python
# coding:utf8

# 以下部分为程序内部逻辑配置，请勿修改
# 无论注册机还是非注册机都要下载的表
common_download_tables = (
    'result_info',
    'card_info',
    'person_info',    
    'class',
    'template',
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
    'person_extra',
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
    'record':'uuid',
}

field_exclude = {
    'person_info':('person_id', 'password'), #没有处理这个会有潜在的bug风险
    #'person_extra':('person_id'),
    'card_info':('person_id','person_uuid'),
    'class':('person_id','class_id'),
    'sample':('person_id','class_id', 'sample_id'),
    'template':('person_id','class_id', 'sample_id', 'template_id'),
    'record':('person_id','class_id','sample_id','record_id', 'template_id'),
}

import plugin
plugins = {
    'card_info':plugin.CardInfoPlugin,
    'class':plugin.ClassPlugin,
    'sample':plugin.SamplePlugin,
    'template':plugin.TemplatePlugin,
    'person_extra':plugin.PersonExtraPlugin,
    'result_info':plugin.ResultInfoPlugin,
}

import serverplugin
serverplugins = {
    'person_extra':serverplugin.PersonExtraPlugin,
    'result_info':serverplugin.ResultInfoPlugin,
    'record':serverplugin.RecordPlugin,
}