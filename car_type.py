# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 01:09:11 2026

@author: HP
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 2026
@author: Gemini
"""


from classes.gclass import Gclass

class Car(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    
    # Lista de nomes de atributos, o identificador deve ser o primeiro e chamar-se 'id'
    # Inclui 'car_type' conforme solicitado para corresponder ao Excel
    att = ['_id', '_description', '_car_type']
    
    # Título do cabeçalho da classe
    header = 'Cars'
    
    # Descrição dos campos para formulários de entrada
    des = ['Id', 'Description', 'Car_Type']

    def __init__(self, id, description, car_type):
        super().__init__()
        
        # Atribuição de ID (usando o método da classe base se disponível)
        if id is None:
            self._id = Car.get_id()
        else:
            self._id = id
            
        self._description = description
        
        # car_type vindo do Excel (ex: 1 ou 2)
        self._car_type = int(car_type) if car_type else 0
        
        # Adicionar o novo objeto ao dicionário de objetos
        Car.obj[self._id] = self
        # Adicionar o id à lista de ids de objetos
        Car.lst.append(self._id)

    @property
    def id(self):
        return self._id

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def car_type(self):
        return self._car_type

    @car_type.setter
    def car_type(self, car_type):
        self._car_type = int(car_type)