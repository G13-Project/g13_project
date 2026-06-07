from classes.company import Company         
from classes.gclass import Gclass


class Car(Gclass):
    obj = {}
    lst = []
    pos = 0
    sortkey = ''

    # Attribute names list, identifier attribute must be the first one and called 'id'
    att = ['_id', '_description', '_id_company', '_car_type']
    # Class header title
    header = 'Car'
    # field description for use in, for example, input form
    des = ['Id', 'Description', 'Id_Company', 'Car_Type']

    # Constructor: Called when an object is instantiated
    def __init__(self, id, description, id_company, car_type):
        super().__init__()

        try:
            id_company = int(id_company)
        except ValueError:
            raise ValueError("id_company must be integer")

        if id_company not in Company.lst:
            raise ValueError(f"Company {id_company} not found")

        self._id = Car.get_id(id)
        self._description = description
        self._id_company = id_company
        self._car_type = car_type   

        Car.obj[self._id] = self
        Car.lst.append(self._id)

    # Properties
    
    @property
    def id(self):
        return self._id
    # Id não tem setter porque a sua mudança causaria problemas para encontrar o objeto

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def car_type(self):
        if self._car_type == 1:
            return "Company's vehicle"
        elif self._car_type == 2:
            return "Personal vehicle"
        return "Unknown"
    
    @car_type.setter
    def car_type(self, new):
         if new == 1 or new == 2:
             self._car_type = new

    @property
    def id_company(self):
        return self._id_company

    @id_company.setter
    def id_company(self, value):
        if value not in Company.lst:
            raise ValueError(f"Company {value} not found")
        self._id_company = value
