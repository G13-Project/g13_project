import datetime
from classes.gclass import Gclass

class Customer(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    # Attribute names list, identifier attribute must be the first one and callled 'id'
    att = ['_id', '_name', '_email', '_phone', '_date_of_birth', '_photo']
    # Class header title
    header = 'Customer'
    # field description for use in, for example, input form
    des = ['Id', 'Name', 'Email', 'Phone', 'Date_Of_Birth', 'Photo']
    
    # Constructor: Called when an object is instantiated
    def __init__(self, id, name, email, phone, date_of_birth, photo=None):
        super().__init__()

        # Object attributes
        id = Customer.get_id(id)
        self._id = id
        self._name = name
        self._email = email
        self._phone =phone
        self._photo = photo

        if date_of_birth:
            try:
                # formato do formulário (dd/mm/YYYY)
                self._date_of_birth = datetime.datetime.strptime(date_of_birth, "%d/%m/%Y").date()
            except:
                try:
                    # formato ISO vindo da DB (YYYY-MM-DD)
                    self._date_of_birth = datetime.date.fromisoformat(date_of_birth)
                except:
                    self._date_of_birth = None
        else:
            self._date_of_birth = None
       
        # Add the new object to the dictionary of objects
        Customer.obj[self._id] = self
        # Add the id to the list of object ids
        Customer.lst.append(id)

    @classmethod
    def insert(cls, code):
        obj = cls.obj[code]

        import sqlite3
        from data.datafile import filename

        conn = sqlite3.connect(filename + 'g13_ridesharing.db')
        cursor = conn.cursor()

        cursor.execute(
    "INSERT INTO Customer (id, name, email, phone, date_of_birth, photo) VALUES (?, ?, ?, ?, ?, ?)",
    (obj.id, obj.name, obj.email, obj.phone, obj.date_of_birth, obj.photo)
)

        conn.commit()
        conn.close()

    # Properties
    
    @property
    def id(self):
        return self._id
    # Id não tem setter porque a sua mudança causaria problemas para encontrar o objeto

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
        
    @classmethod
    def read(cls, db_path):
        cls.obj = dict()
        cls.lst = list()

        import sqlite3
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Garantir que a coluna photo existe na base de dados
            try:
                cursor.execute("ALTER TABLE Customer ADD COLUMN photo TEXT")
                conn.commit()
            except:
                pass

            cursor.execute("SELECT * FROM Customer")
            rows = cursor.fetchall()

            for row in rows:
                cls(*row)   

            conn.close()

        except Exception as e:
            print(f"Erro ao ler tabela Customer: {e}")

    @property
    def date_of_birth(self):
        if self._date_of_birth:
            return self._date_of_birth.strftime("%d/%m/%Y")
        return None
    @date_of_birth.setter
    def date_of_birth(self, date_of_birth):
        self._date_of_birth = datetime.datetime.strptime(date_of_birth, "%d/%m/%Y").date()

    @property
    def photo(self):
        return self._photo
    @photo.setter
    def photo(self, photo):
        self._photo = photo

    @classmethod
    def update(cls, code):
        obj = cls.obj[code]

        import sqlite3
        from data.datafile import filename

        conn = sqlite3.connect(filename + 'g13_ridesharing.db')
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Customer
            SET name = ?, email = ?, phone = ?, date_of_birth = ?, photo = ?
            WHERE id = ?
        """, (
            obj.name,
            obj.email,
            obj.phone,
            obj.date_of_birth,
            obj.photo,
            obj.id
        ))

        conn.commit()
        conn.close()
    
