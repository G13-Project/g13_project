# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 14:39:11 2026

@author: up202507606
"""
from classes.company import Company
from classes.driver import Driver
from classes.customer import Customer
from classes.car import Car


import datetime
# Class Ride - generic version with inheritance
from gclass import Gclass

class Ride(Gclass):
    velocidade = {'Rápido': ["Speed Enthusiast", "Shortcut Sorcerer"], 'Calmo':['Silent Cruiser','Chill Navigator'], 'Fluído': ['Smooth Operator','Efficiency Expert'] }

    Segurança = {'Máxima': ['Safety Sentinel'], 'Suave': ['Smooth Operator','Zen Driver'], 'Sem preocupações': ['Silent Cruiser', 'Road Philosopher']}

    Horário = {"Manhã":["Early Bird", "Zen Driver"],"Noite":["Night Owl", "Zen Driver"]}

    Tecnologia = {'Avançada': ['Tech-Obsessed Pilot'], 'Fiel': ['GPS Purist'], 'Instintivo': ['Efficiency Expert', 'Shortcut Sorcerer']}
    
    ambiente = {'Silêncio': ['Silent Cruiser'], 'Calmo': ['Zen Driver', 'Chill Navigator', 'Road Philosopher', 'Snack Provider'], 'Animado': ['Vibe setter', 'Playist Maestro', 'Snack Provider']}

    iteracao = {'Reduzida': ['Silent Cruiser'],'Moderada': ['Conversation Curator', 'Snack Provider', 'Friendly Neighbour'],'Elevada': ['Road Philosopher', 'Storyteller', 'Snack Provider']}

    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    # Attribute names list, identifier attribute must be the first one and callled 'id'
    att = ['_id', '_id_company', '_id_driver', '_id_customer', '_id_car', '_origin', '_destination', '_ride_date','_amount']
    # Class header title
    header = 'Ride'
    # field description for use in, for example, input form
    des = ['Id','Id Company','Id Driver','Id Customer','Id Car','Origin','Destination','Ride Date','Amount']

    # Constructor: Called when an object is instantiated
    def __init__(self, id, id_company, id_driver, id_customer, id_car, origin, destination, ride_date, amount):
        super().__init__()

        try:
            id_company = int(id_company)
            id_car = int(id_car)
            id_customer = int(id_customer)
            id_driver = int(id_driver)
        except: 
            pass

        self._id = Ride.get_id(id)
      
        try:
            self._ride_date = datetime.date.fromisoformat(str(ride_date)[:10])
        except:
            self._ride_date = datetime.date.today()
        if id_company not in Company.lst:
            raise ValueError(f"Company {id_company} not found")
        if id_driver not in Driver.lst:
            raise ValueError(f"Driver {id_driver} not found")
        if id_customer not in Customer.lst:
            raise ValueError(f"Customer {id_customer} not found")
        if id_car not in Car.lst:
            raise ValueError(f"Car {id_car} not found")

        self._id_company = id_company
        self._id_driver = id_driver
        self._id_customer = id_customer
        self._id_car = id_car
        self._origin = origin
        self._destination = destination
        self._amount = amount

    
       #For memory
        Ride.obj[self._id] = self
        Ride.lst.append(self._id)
        
    @property    
    def id_customer(self):
        return self._id_customer
    @property
    def id_driver(self):
        return self._id_driver
    @property
    def id_company(self):
        return self._id_company
    @property
    def id_car(self):
        return self._id_car
    @property
    def id(self):
        return self._id
    @property
    def origin(self):
        return self._origin
    @origin.setter
    def origin(self, origin):
        self._origin = origin
    @property
    def destination(self):
        return self._destination
    @destination.setter
    def destination(self, destination):
        self._destination = destination
    @property
    def ride_date(self):
        return self._ride_date
    @ride_date.setter
    def ride_date(self, ride_date):
        self._ride_date =datetime.date.fromisoformat(ride_date)
    @property
    def amount(self):
        return self._amount
    @amount.setter
    def amount(self, amount):
        self._amount = amount
