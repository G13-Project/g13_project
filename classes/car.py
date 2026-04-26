from gclass import Gclass

class Car(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    att = ['_id','_description','_id_company','_car_type']
    header = 'Car' 
    des = ['Id','Description','id_company','Car_type']

    # A ordem dos atributos deve ser id, description, id_company, car_type
    att = ['_id', '_description', '_id_company', '_car_type']
    
    def __init__(self, id, description, id_company, car_type):
        super().__init__()
        self._id = Car.get_id(id)
        self._description = description
        self._id_company = int(id_company)
        self._car_type = int(car_type) 
        
        Car.obj[self._id] = self
        Car.lst.append(self._id)
        
    @property
    def id(self):
        return self._id

    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self, new):
        self._description = new

    @property
    def car_type(self):
        if self._car_type == 1:
            return "Veículo da empresa"
        elif self._car_type == 2:
            return "Veículo pessoal"
        return self._car_type

    @property
    def id_company(self):
        return self._id_company

    @id_company.setter
    def id_company(self, newid):
        self._id_company = newid