
from gclass import Gclass
import datetime
class Driver(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    # Attribute names list, identifier attribute must be the first one and callled 'id'
    att = ['_id','_nickname','_driver_type']
    # Class header title
    header = 'Driver'
    # field description for use in, for example, input form
    des = ['Id','Nickname','Drivertype']
    # Constructor: Called when an object is instantiated
    def __init__(self, id, nickname, driver_type):
        super().__init__()
        # Object attributes
        id = Driver.get_id(id)
        self._id = id
        self._nickname = nickname
        self._driver_type = driver_type
        
        # Add the new object to the dictionary of objects
        Driver.obj[self._id] = self
        # Add the id to the list of object ids
        Driver.lst.append(self._id)
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
    def driver_type(self):
        return self._driver_type
    # type property setter method
    @driver_type.setter
    def driver_type(self, type):
        self._driver_type = type

