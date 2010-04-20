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
    def postUploadData(self, data):
        self.db.genOneResult(data['person_id'], data['person_uuid'])
        return data
    
class ResultInfoPlugin(ServerPluginAbstract):
    def preUploadData(self, data):
        r = self.db.getOneResult('select person_id from person_info where uuid = "%s"' % data['person_uuid'])
        if not r:
            data['person_id'] = None
            return data
        data['person_id'] = r['person_id']
        return data
        
class RecordPlugin(ServerPluginAbstract):
    def preUploadData(self, data):
        if (data['result'] == '22'):
            r = self.db.getOneResult('select * from record where person_uuid = "%s" and date(time) = date("%s") and result = 22' % (data['person_uuid'], data['time']))
            if r:
                data['result'] = 5
        return data
    def postUploadData(self, data):
        if (data['result'] == '21'):
            self.db.executeSQL('update result_info set sync=current_timestamp, total_mor=total_mor+1 where person_uuid = "%s"' % data['person_uuid'])
        elif (data['result'] == '22'):
            self.db.executeSQL('update result_info set sync=current_timestamp, total_eve=total_eve+1 where person_uuid = "%s"' % data['person_uuid'])
        return data