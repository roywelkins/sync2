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
        self.db.executeSQL('update card_info set person_id = (select person_id from person_info where person_info.student_id = card_info.student_id)')
        self.db.executeSQL('update card_info set person_uuid = (select uuid from person_info where person_info.student_id = card_info.student_id)')
