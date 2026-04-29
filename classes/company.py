from gclass import Gclass
import datetime as dt


class Company(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    
    # Attribute names list, identifier attribute must be the first one and callled 'id'
    att = ['_id','_name','_begin_date']
    # Class header title
    header = 'Company'
    # field description for use in, for example, input form
    des = ['Id','Name','Begin_Date']
    
    # Constructor: Called when an object is instantiated
    def __init__(self, id, name, begin_date):
        super().__init__()
        id = Company.get_id(id)
        self._id = id
        self._name = name
        self._begin_date = dt.date.fromisoformat(begin_date)
        Company.obj[id] = self
        Company.lst.append(id)
        
    # id property getter method
    @property
    def id(self):
        return self._id
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        self._name = name
    @property
    def begin_date(self):
        return self._begin_date
    @begin_date.setter
    def begin_date(self, begin_date):
        self._begin_date = dt.date.fromisoformat(begin_date)




