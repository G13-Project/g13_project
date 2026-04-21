"""
@author: António Brito / Carlos Bragança
(2025) objective: class Person
"""
# Class Person - generic version with inheritance
from classes.gclass import Gclass
import datetime
class Person(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    # Attribute names list, identifier attribute must be the first one and callled 'id'
    att = ['_id','_name','_dob','_salary']
    # Class header title
    header = 'Persons'
    # field description for use in, for example, input form
    des = ['Id','Name','Date of Birth','Salary']
    # Constructor: Called when an object is instantiated
    def __init__(self, id, name, dob, salary):
        super().__init__()
        # Object attributes
        id = Person.get_id(id)
        self._id = id
        self._name = name
        self._dob = datetime.date.fromisoformat(dob)
        self._salary = float(salary)
        # Add the new object to the dictionary of objects
        Person.obj[id] = self
        # Add the id to the list of object ids
        Person.lst.append(id)
    # id property getter method
    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, id):
        self._id = id
    # name property getter method
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        self._name = name
    # dob property getter method
    @property
    def dob(self):
        return self._dob
    # dob property setter method
    @dob.setter
    def dob(self, dob):
        self._dob = dob
    # salary property getter method
    @property
    def salary(self):
        return self._salary
    # salary property setter method
    @salary.setter
    def salary(self, salary):
        self._salary = salary
    # age property getter method
    @property
    def age(self):
        tday = datetime.date.today()
        age = tday.year - self.dob.year
        if tday.month < self.dob.month or \
            (tday.month == self.dob.month and tday.day < self.dob.day):
            age -= 1
        return age

