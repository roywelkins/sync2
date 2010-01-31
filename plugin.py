#!/usr/bin/env python


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