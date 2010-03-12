#!/usr/bin/env python
#coding:utf8

class PluginAbstract:
    def __init__(self, db=None):
        self.db = db
    def preUpload(self):
        pass
    def postUpload(self):
        pass
    def preDownload(self):
        pass
    def postDownload(self):
        pass
    def preUploadData(self, data):
        return data
    def postUploadData(self, data):
        return data
    def preDownloadData(self, data):
        return data
    def postDownloadData(self, data):
        return data
    
class CardInfoPlugin(PluginAbstract):
    def postDownload(self):
        self.db.executeSQL('update card_info set person_id = (select person_id from person_info where person_info.student_id = card_info.student_id) where person_id is null')
        self.db.executeSQL('update card_info set person_uuid = (select uuid from person_info where person_info.student_id = card_info.student_id) where person_uuid is null')

class ClassPlugin(PluginAbstract):
    def postDownload(self):
        self.db.executeSQL('update class set person_id = (select person_id from person_info where person_info.uuid = class.person_uuid) where person_id is null')
        
class SamplePlugin(PluginAbstract):
    def postDownload(self):
        self.db.executeSQL('update sample set person_id = (select person_id from person_info where person_info.uuid = sample.person_uuid) where person_id is null')
        self.db.executeSQL('update sample set class_id = (select class_id from class where class.uuid = sample.class_uuid) where class_id is null')
        
class TemplatePlugin(PluginAbstract):
    def postDownload(self):
        self.db.executeSQL('update template set person_id = (select person_id from person_info where person_info.uuid = template.person_uuid) where person_id is null')
        self.db.executeSQL('update template set class_id = (select class_id from class where class.uuid = template.class_uuid) where class_id is null')
        self.db.executeSQL('update template set sample_id = (select sample_id from sample where sample.uuid = template.sample_uuid) where sample_id is null')
        
    def preUploadData(self, data):
        #因为所有待上传是一次性取出的，如果在上传过程中本地又对记录进行了更改，
        #那么这个更改不能体现到服务器上，因此每上传一个数据都进行重新读取
        return self.db.getData('template', 'template_id = %s' % data['template_id'])
        
class PersonExtraPlugin(PluginAbstract):
    def preDownloadData(self, data):
        r = self.db.getOneResult('select person_id from person_info where uuid = "%s"' % data['person_uuid'])
        if not r:
            data['person_id'] = None
            return data
        data['person_id'] = r['person_id']
        return data

class ResultInfoPlugin(PluginAbstract):
    def preDownloadData(self, data):
        r = self.db.getOneResult('select person_id from person_info where uuid = "%s"' % data['person_uuid'])
        if not r:
            data['person_id'] = None
            return data
        data['person_id'] = r['person_id']
        return data