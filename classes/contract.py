import datetime
from classes.company import Company
from classes.driver import Driver
from gclass import Gclass
class Contract(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    # Attribute names list, identifier attribute must be the first one and callled 'id'
    att = ['_id', '_contract_start', '_contract_end', '_id_company', '_id_driver']
    # Class header title
    header = 'Contract'
    # field description for use in, for example, input form
    des = ['Id', 'Contract_Start', 'Contract_End', 'Id_Company', 'Id_Driver']
    # Constructor: Called when an object is instantiated
    def __init__(self, id, contract_start, contract_end, id_company, id_driver):
        super().__init__()
        if id_company not in Company.lst:
            raise ValueError(f"Company {id_company} not found")
        if id_driver not in Driver.lst:
            raise ValueError(f"Driver {id_driver} not found") 
        
        self._id = Contract.get_id(id) 
        
        try:
            self._contract_start = datetime.date.fromisoformat(contract_start[:10])
            self._contract_end = (datetime.date.fromisoformat(contract_end[:10]) if contract_end else "Vitalício")
        except Exception as e:
            #in case the format is strange
            print(f"Erro na data do contrato {id}: {e}")
            self._contract_start = datetime.date.today() 
            self._contract_end = None

            
        # saving the IDs in memory
        self._id_company = id_company
        self._id_driver = id_driver
        
        # add to list
        Contract.obj[self._id] = self
        Contract.lst.append(self._id)
        
        
    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, id):
        self._id = id
    @property
    def contract_start(self):
        return self._contract_start
    @contract_start.setter
    def contract_start(self, contract_start):
        self._contract_start = contract_start
    @property
    def contract_end(self):
        return self._contract_end
    @contract_end.setter
    def contract_end(self, contract_end):
        self._contract_end = contract_end
    @property
    def id_company(self):
        return self._id_company
    @property
    def id_driver(self):
        return self._id_driver
