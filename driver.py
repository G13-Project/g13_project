from classes.gclass import Gclass
import datetime
class Driver(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    # Attribute names list, identifier attribute must be the first one and callled 'id'
    att = ['_id','_nickname','_type']
    # Class header title
    header = 'Driver'
    # field description for use in, for example, input form
    des = ['Id','Nickname','Type']
    # Constructor: Called when an object is instantiated
    def __init__(self, id, nickname, type):
        super().__init__()
        # Object attributes
        id = Driver.get_id(id)
        self._id = id
        self._nickname = nickname
        self._type = type
        
        # Add the new object to the dictionary of objects
        Driver.obj[id] = self
        # Add the id to the list of object ids
        Driver.lst.append(id)
    # id property getter method
    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, id):
        self._id = id
    # nickname property getter method
    @property
    def nickname(self):
        return self._nickname
    @nickname.setter
    def nickname(self, nickname):
        self._nickname = nickname

    # type property getter method
    @property
    def type(self):
        return self._type
    # type property setter method
    @type.setter
    def type(self, type):
        self._type = type

