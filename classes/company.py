from classes.gclass import Gclass
import datetime as dt


class Company(Gclass):
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''
    
    # Attribute names list, identifier attribute must be the first one and callled 'id'
    att = ['_id','_name','_begin_date', '_photo']
    # Class header title
    header = 'Company'
    # field description for use in, for example, input form
    des = ['Id','Name','Begin_Date', 'Photo']
    
    # Constructor: Called when an object is instantiated
    def __init__(self, id, name, begin_date, photo=None):
        super().__init__()
        id = Company.get_id(id)
        self._id = id
        self._name = name
        self._begin_date = dt.datetime.strptime(begin_date, "%d/%m/%Y").date()
        self._photo = photo

        Company.obj[id] = self
        Company.lst.append(id)
        
    # id property getter method
    @property
    def id(self):
        return self._id
    
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        self._name = name
        
    @property
    def begin_date(self):
        return self._begin_date.strftime("%d/%m/%Y")
    @begin_date.setter
    def begin_date(self, begin_date):
        self._begin_date = dt.datetime.strptime(begin_date, "%d/%m/%Y").date()

    @property
    def photo(self):
        return self._photo
    @photo.setter
    def photo(self, photo):
        self._photo = photo

    @classmethod
    def insert(cls, code):
        obj = cls.obj[code]

        import sqlite3
        from data.datafile import filename

        conn = sqlite3.connect(filename + 'g13_ridesharing.db')
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO Company (id, name, begin_date, photo) VALUES (?, ?, ?, ?)",
            (obj.id, obj.name, obj.begin_date, obj.photo)
        )

        conn.commit()
        conn.close()
    def lucro(self):
        from classes.ride import Ride
        total = 0
        for ride_id in Ride.lst:
            ride = Ride.obj[ride_id]

            
            if ride.id_company == self.id:
                try:
                    total += float(ride.amount)
                except:
                    pass

        return round(0.20 * total,2)
        

    @classmethod
    def update(cls, code):
        obj = cls.obj[code]

        import sqlite3
        from data.datafile import filename

        conn = sqlite3.connect(filename + 'g13_ridesharing.db')
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Company
            SET name = ?, begin_date = ?, photo = ?
            WHERE id = ?
        """, (
            obj.name,
            obj.begin_date,
            obj.photo,
            obj.id
        ))

        conn.commit()
        conn.close()
