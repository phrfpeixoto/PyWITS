import string

class identifier:
    def __init__(self,record_identifier=None,item_identifier=None):
        self.record_identifier = record_identifier
        self.item_identifier = item_identifier

    def get_full_id(self):
        return self.record_identifier + self.item_identifier

    full = property(get_full_id)

    def __repr__(self):
        return '%s%s' % (self.record_identifier, self.item_identifier)

class data_record:
    def __init__(self,identifier=None,value=None):
        self.identifier = identifier
        self.value = value

    def __repr__(self):
        return 'DR: Id: %s V: %s' % (repr(self.identifier),str(self.value))

class logical_record:
    def __init__(self,data_records=[]):
        self.data_records = data_records
        
    def __repr__(self):
        d = ['Logical Record:']
        for dr in self.data_records:
            d.append(repr(dr))

        return string.join(d,'\n')
        
        