import datetime
# Class Customer - generic version with inheritance
from gclass import Gclass
class Customer(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    # Attribute names list, identifier attribute must be the first one and callled 'id'
    att = ['_id', '_name', '_email', '_phone', '_date_of_birth']
    # Class header title
    header = 'Customer'
    # field description for use in, for example, input form
    des = ['Id', 'Name', 'Email', 'Phone', 'Date_Of_Birth']
    # Constructor: Called when an object is instantiated
    def __init__(self, id, name, email, phone, date_of_birth):
        super().__init__()
        # Object attributes
        id = Customer.get_id(id)
        self._id = id
        self._name = name
        self._email = email
        self._phone =phone
        self._date_of_birth = datetime.date.fromisoformat(date_of_birth)
        # Add the new object to the dictionary of objects
        Customer.obj[self._id] = self
        # Add the id to the list of object ids
        Customer.lst.append(id)
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
    def email(self):
        return self._email
    @email.setter
    def email(self, email):
        self._email = email
    @property
    def phone(self):
        return self._phone
    @phone.setter
    def phone(self, phone):
        self._phone = phone
    @property
    def date_of_birth(self):
        return self._date_of_birth
    @date_of_birth.setter
    def date_of_birth(self, date_of_birth):
        self._date_of_birth = datetime.date.fromisoformat(date_of_birth)