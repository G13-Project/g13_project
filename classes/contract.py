import datetime
from classes.company import Company
from classes.driver import Driver
from classes.gclass import Gclass

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
            self._contract_start = datetime.datetime.strptime(contract_start, "%d/%m/%Y %H:%M:%S")

            if contract_end:
                self._contract_end = datetime.datetime.strptime(contract_end, "%d/%m/%Y %H:%M:%S")
            else:
                self._contract_end = None

            # Validação lógica
            if self._contract_end is not None and self._contract_end < self._contract_start:
                raise ValueError("A data final não pode ser anterior à data inicial")

        except ValueError as e:
            raise ValueError(f"Erro no contrato {id}: {e}")

        # Guardar IDs
        self._id_company = id_company
        self._id_driver = id_driver

        # Guardar em memória
        Contract.obj[self._id] = self
        Contract.lst.append(self._id)
        
    @property
    def id(self):
        return self._id
    # Id não tem setter porque a sua mudança causaria problemas para encontrar o objeto
    
    @property
    def contract_start(self):
        return self._contract_start.strftime("%d/%m/%Y %H:%M:%S")
    # Contract_start não tem setter porque não faz sentido o início de um contrato mudar
    
    # Assume-se que contract_end = None é um contrato vitalício
    @property
    def contract_end(self):
        if self._contract_end is None:
            return "Vitalício"
        else:
            return self._contract_end.strftime("%d/%m/%Y %H:%M:%S")

    # Aceita formatos datetime, string e None
    @contract_end.setter
    def contract_end(self, contract_end):

        # string -> converter
        if isinstance(contract_end, str):
            try:
                contract_end = datetime.datetime.strptime(contract_end, "%d/%m/%Y %H:%M:%S")

            except ValueError:
                raise ValueError("Formato inválido. Use DD/MM/YYYY H:M:S")

        # Se não vier num formato válido (data, string ou None) dá erro
        elif not(isinstance(contract_end, datetime.date)) and not(contract_end is None):
            raise TypeError("contract_end deve ser str, datetime.date ou None")

        # Validação lógica
        if contract_end is not None and contract_end < self._contract_start:
            raise ValueError("A data final não pode ser anterior à data inicial")

        # Guardar
        self._contract_end = contract_end


    @property
    def id_company(self):
        return self._id_company
    @property
    def id_driver(self):
        return self._id_driver
    
    # Serve para despedir um trabalhador na data fornecida (assumida como a de hoje se for omitida)
    def terminate(self, data_fim = None):
        if data_fim is None:
            data_fim = datetime.datetime.now()

        self.contract_end = data_fim
        
    # Determina se um contrato está ativo (retorna True ou False)
    @property
    def is_active(self):
        today = datetime.datetime.now()
        
        if (self._contract_end is None or today >= self._contract_end) and today >= self._contract_start:
            return True
        
        else:
            return False

    

