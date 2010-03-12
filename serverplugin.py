#!/usr/bin/env python

class ServerPluginAbstract:
    def __init__(self, db=None):
        self.db = db
    def preUploadData(self, data):
        return data
    def postUploadData(self, data):
        return data
    def preDownloadData(self, data):
        return data
    def postDownloadData(self, data):
        return data
    def preUploadTable(self):
        pass
    def postUploadTable(self):
        pass
    def preDownloadTable(self):
        pass
    def postDownloadTable(self):
        pass
    
class PersonExtraPlugin(ServerPluginAbstract):
    def preUploadData(self, data):
        r = self.db.getOneResult('select person_id from person_info where uuid = "%s"' % data['person_uuid'])
        if not r:
            data['person_id'] = None
            return data
        data['person_id'] = r['person_id']
        return data
    
class ResultInfoPlugin(ServerPluginAbstract):
    def preUploadData(self, data):
        r = self.db.getOneResult('select person_id from person_info where uuid = "%s"' % data['person_uuid'])
        if not r:
            data['person_id'] = None
            return data
        data['person_id'] = r['person_id']
        return data
        