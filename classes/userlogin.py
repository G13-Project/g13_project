import sqlite3
import bcrypt
from classes.gclass import Gclass

class Userlogin(Gclass):
    obj = {}
    lst = []
    pos = 0
    db_path = None

    att = ['_id', '_user', '_usergroup', '_password']
    header = 'Users'

    # -------- CONSTRUCTOR --------
    def __init__(self, id, user, usergroup, password):
        super().__init__()

        if id == 0:
            id = len(Userlogin.lst) + 1

        self._id = id
        self._user = user
        self._usergroup = usergroup
        self._password = password

        Userlogin.obj[id] = self
        Userlogin.lst.append(id)

    # -------- PROPERTIES --------
    @property
    def id(self):
        return self._id

    @property
    def user(self):
        return self._user

    @property
    def usergroup(self):
        return self._usergroup

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    # -------- DATABASE --------
    @classmethod
    def read(cls, db_path):
        cls.db_path = db_path
        cls.obj = {}
        cls.lst = []

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users(
            id INTEGER PRIMARY KEY,
            user TEXT UNIQUE,
            usergroup TEXT,
            password TEXT
        )
        """)

        cursor.execute("SELECT * FROM Users")
        rows = cursor.fetchall()

        for row in rows:
            cls(*row)

        conn.close()

    @classmethod
    def insert(cls, code):
        obj = cls.obj[code]

        conn = sqlite3.connect(cls.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO Users (id, user, usergroup, password) VALUES (?, ?, ?, ?)",
            (obj.id, obj.user, obj.usergroup, obj.password)
        )

        conn.commit()
        conn.close()

    @classmethod
    def update(cls, code):
        obj = cls.obj[code]

        conn = sqlite3.connect(cls.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE Users SET user=?, usergroup=?, password=? WHERE id=?",
            (obj.user, obj.usergroup, obj.password, obj.id)
        )

        conn.commit()
        conn.close()

    # -------- SEARCH --------
    @classmethod
    def find(cls, value, field):
        result = []
        for id in cls.lst:
            obj = cls.obj[id]
            if getattr(obj, field) == value:
                result.append(obj)
        return result

    # -------- LOGIN --------
    @classmethod
    def get_user_id(cls, user):
        users = cls.find(user, 'user')
        if len(users) == 1:
            return users[0].id
        return 0

    @classmethod
    def chk_password(cls, user, password):
        user_id = cls.get_user_id(user)

        if user_id == 0:
            return "User does not exist"

        obj = cls.obj[user_id]

        if bcrypt.checkpw(password.encode(), obj._password.encode()):
            return "Valid"
        else:
            return "Wrong password"

    @classmethod
    def set_password(cls, password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    @classmethod #Para saber a que grupo pertence
    def get_role(cls, user):
        user_id = cls.get_user_id(user)

        if user_id == 0:
            return None

        obj = cls.obj[user_id]
        return obj.usergroup


    # -------- PRINT --------
    def __str__(self):
        return f"ID:{self.id}, User:{self.user}, Group:{self.usergroup}"
