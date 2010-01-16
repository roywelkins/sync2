#!/usr/bin/env python
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

class XMLManager:
    """deal with xml file generation"""
    
    def dictToXML(self, datadict, head):
        root = ElementTree.Element(head)
        for key, value in datadict.items():            
            if type(value)==dict:
                root.append(self.dictToXML(value, key))
            else:
                e = ElementTree.Element(key)
                if type(value)==str:
                    e.text = value.decode('utf8')
                else:
                    e.text = unicode(value)
                root.append(e)
        return root