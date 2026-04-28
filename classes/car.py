# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 10:19:41 2026

@author: Joao M Braga
"""

#%%

# Class Car  
from company import Company 
from classes.gclass import Gclass
class Car(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    # Attribute names list, identifier attribute must be the first one and callled 'id'
    att = ['_id','_description','_id_company','_car_type']
    # Class header title
    header = 'Car'
    # field description for use in, for example, input form
    des = ['Id','Description','Id_company','Car_type']
    # Constructor: Called when an object is instantiated
    def __init__(self, id, description, id_company, car_type):
        super().__init__()
        # Check the company referencial integrity
        id_company = int(id_company)
        if id_company in Company.lst:
            id = Car.get_id(id)
            # Object attributes
            self._id = id
            self._description = description
            self._id_company = int(id_company)
            self._car_type = car_type
            # Add the new object to the Car List
            Car.obj[id] = self
            # Add the id to the list of object ids
            Car.lst.append(id)
        else:
            print(f"Company {id_company} not found")

    #Object properties
    # id property getter method
    @property
    def id(self):
        return self._id
    # description property getter and setter method
    @property
    def description(self):
        return self._description
    @description.setter
    def description(self, new):
        self._description = new
    # car_type property getter and setter method
    @property
    def car_type(self):
        if self._car_type == 1:
            return "Veículo da empresa"
        elif self._car_type == 2:
            return "Veículo pessoal"
    @car_type.setter
    def car_type(self, new):
        if new == 1 or new == 2:
            self._car_type = new
    # id_company property getter and setter method
    @property
    def id_company(self):
        return self._id_company
    @id_company.setter
    def id_company(self, newid):
        if newid in Company.lst:
            self._id_company = newid
        else:
            print(f"Company {newid} not found")
