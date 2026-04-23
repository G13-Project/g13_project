# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 10:19:41 2026

@author: Joao M Braga
"""

#%%

# Class Car
from classes.gclass import Gclass
class Car(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    # Attribute names list, identifier attribute must be the first one and callled 'id'
    att = ['_id','_description','_company_id']
    # Class header title
    header = 'Cars'
    # field description for use in, for example, input form
    des = ['Id','Description','Company_id']
    # Constructor: Called when an object is instantiated
    def __init__(self, id, company_id, description):
        super().__init__()
        # Check the company referencial integrity
        company_id = int(company_id)
        if company_id in Company.lst:
            id = Car.get_id(id)
            # Object attributes
            self._id = id
            self._description = description
            self._company_id = company_id
            # Add the new object to the Car List
            Car.obj[id] = self
            # Add the id to the list of object ids
            Car.lst.append(id)
        else:
            print(f"Company {company_id} not found")

    #Object properties
    # id property getter and setter method
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
    # id_company property getter and setter method
    @property
    def company_id(self):
        return self._company_id
    @company_id.setter
    def company_id(self, newid):
        if newid in Company.lst:
            self._company_id = newid
        else:
            print(f"Company {company_id} not found")