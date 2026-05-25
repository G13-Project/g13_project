import sqlite3

class Gclass:
    obj = dict()     
    lst = list()     
    pos = 0          
    att = []         
    header = ''     
    des = []         

    def __init__(self):
        pass

    def __str__(self):
        """Retorna uma string com os valores dos atributos do objeto"""
        s = ""
        for at in self.att:
            s += str(getattr(self, at)) + ";"
        return s[:-1]


    @classmethod
    def get_id(cls, id):
        """Gera um ID automático se o fornecido for None ou vazio"""
        if id in [None, 'None', '']:
            if len(cls.lst) == 0:
                return 1
            else:
                return max(map(int, cls.lst)) + 1
        return int(id)

   
    @classmethod
    def read(cls, db_path):
        """Lê os dados da tabela correspondente na base de dados SQLite"""
        cls.obj = dict()
        cls.lst = list()

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute(f"SELECT * FROM {cls.header}")
            rows = cursor.fetchall()

            for row in rows:
                cls(*row)   

            conn.close()

        except Exception as e:
            print(f"Erro ao ler tabela {cls.header}: {e}")

  
    @classmethod
    def first(cls):
        cls.pos = 0

    @classmethod
    def last(cls):
        cls.pos = len(cls.lst) - 1

    @classmethod
    def nextrec(cls):
        if cls.pos < len(cls.lst) - 1:
            cls.pos += 1

    @classmethod
    def previous(cls):
        if cls.pos > 0:
            cls.pos -= 1

    @classmethod
    def current(cls):
        if len(cls.lst) > 0:
            code = cls.lst[cls.pos]
            return cls.obj[code]
        return None

   
    @classmethod
    def remove(cls, code):
        """Remove um objeto da memória pelo seu ID"""
        if code in cls.obj:
            del cls.obj[code]
            cls.lst.remove(code)
            cls.pos = 0


    @classmethod
    def sort(cls, attrib, reverse=False):
        """Ordena a lista de IDs por um determinado atributo"""
        cls.lst.sort(key=lambda x: getattr(cls.obj[x], '_' + attrib), reverse=reverse)
        cls.pos = 0


    @classmethod
    def find(cls, value, attrib):
        """Procura objetos que tenham um determinado valor num atributo"""
        results = []
        for code in cls.lst:
            if getattr(cls.obj[code], '_' + attrib) == value:
                results.append(cls.obj[code])
        return results
