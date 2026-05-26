from classes.gclass import Gclass 
import ast


class Driver(Gclass): 
    obj = dict() 
    lst = list() 
    pos = 0 
    sortkey = '' 
    # Attribute names list, identifier attribute must be the first one and callled 'id' 
    att = ['_id','_nickname','_driver_type', '_ratings'] 
    # Class header title 
    header = 'Driver' 
    # field description for use in, for example, input form 
    des = ['Id','Nickname','Drivertype', 'Ratings'] 
    # Constructor: Called when an object is instantiated 
     

        
    def __init__(self, id, nickname, driver_type, ratings=None):
        super().__init__()
    
        id = Driver.get_id(id)
        self._id = id
        self._nickname = nickname
        self._driver_type = driver_type
    
        if isinstance(ratings, str):
            self._ratings = ast.literal_eval(ratings)
        else:
            self._ratings = ratings if ratings is not None else []
    
        Driver.obj[self._id] = self
        Driver.lst.append(self._id)

    # id property getter method 
    @property 
    def id(self): 
        return self._id 

    # nickname property getter method 
    @property 
    def nickname(self): 
        return self._nickname 

    @nickname.setter 
    def nickname(self, nickname): 
        self._nickname = nickname 
 
    # type property getter method 
    @property 
    def driver_type(self): 
        return self._driver_type 

    # type property setter method 
    @driver_type.setter 
    def driver_type(self, type): 
        self._driver_type = type 
      

    @property 
    def ratings(self): 
        return self._ratings 

    @ratings.setter 
    def ratings(self, ratings): 
        self._ratings = ratings 
 

    def evaluate(self, rating): 
        if 1 <= rating <= 5: 
            self._ratings.append(rating) 

    def average_ratings(self): 
        if len(self._ratings) == 0: 
            return 0 
        return sum(self._ratings) / len(self._ratings)
