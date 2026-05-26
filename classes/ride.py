from classes.company import Company
from classes.driver import Driver
from classes.customer import Customer
from classes.car import Car
from classes.gclass import Gclass

import datetime
import requests


def geocode(address):
    
    try:
        url = "https://photon.komoot.io/api/"
        params = {"q": address, "limit": 1}
        r = requests.get(url, params=params, timeout=5)
        data = r.json()

        if data["features"]:
            coords = data["features"][0]["geometry"]["coordinates"]
            return f"{coords[0]},{coords[1]}"
    except:
        pass

    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json", "limit": 1}
        r = requests.get(url, params=params, headers={"User-Agent": "PC2-Project"})
        data = r.json()

        if data:
            return f"{data[0]['lon']},{data[0]['lat']}"
    except:
        pass

    return None


def fallback_distance_time(origin, destination):
    estimativas = {
        ("Porto, Portugal", "Lisbon, Portugal"): (310, 180),
        ("Lisbon, Portugal", "Porto, Portugal"): (310, 180),
        ("Porto, Portugal", "Maia, Portugal"): (12, 20),
        ("Maia, Portugal", "Porto, Portugal"): (12, 20)
    }

    return estimativas.get((origin, destination), (50, 60))

def get_distance_and_time(origin_str, destination_str):
    if not origin_str or not destination_str:
        raise ValueError("Origem e destino são obrigatórios")

    origin = geocode(origin_str)
    destination = geocode(destination_str)

    if origin is None or destination is None:
        raise ValueError("Erro ao geocodificar endereços")

    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{origin};{destination}?overview=false"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if "routes" not in data or not data["routes"]:
            raise ValueError("Nenhuma rota encontrada")

        route = data["routes"][0]

        distance_km = route["distance"] / 1000
        duration_min = route["duration"] / 60

      
        if distance_km <= 0 or duration_min <= 0:
            raise ValueError("Valores inválidos")

        if distance_km > 1000 or duration_min > 1000:
            raise ValueError("Rota irrealista")

        return round(distance_km, 2), round(duration_min, 2)

    except (requests.RequestException, KeyError, ValueError) as e:
        print("Erro na API:", e)

        return fallback_distance_time(origin_str, destination_str)



class Ride(Gclass):
 
    Velocidade = {
        'Rápido': ["Speed Enthusiast", "Shortcut Sorcerer"],
        'Calmo':['Silent Cruiser','Chill Navigator', "Zen Driver"], 
        'Fluído': ['Smooth Operator','Efficiency Expert'] 
    }

    Segurança = {
        'Máxima': ['Safety Sentinel'],
        'Suave': ['Smooth Operator','Zen Driver'],
        'Sem preocupações': ['Silent Cruiser', 'Road Philosopher']
    }

    Horário = {
        "Manhã":["Early Bird", "Zen Driver"],
        "Noite":["Night Owl", "Zen Driver", "Road Philosopher"]
    }

    Tecnologia = {
        'Avançada': ['Tech-Obsessed Pilot'],
        'Fiel': ['GPS Purist'],
        'Instintivo': ['Efficiency Expert', 'Shortcut Sorcerer']
    }

    Ambiente = {
        'Silêncio': ['Silent Cruiser'],
        'Calmo': ['Zen Driver', 'Chill Navigator', 'Road Philosopher', 'Snack Provider'],
        'Animado': ['Vibe setter', 'Playist Maestro', 'Snack Provider']
    }

    Interacao = {
        'Reduzida': ['Silent Cruiser'],
        'Moderada': ['Conversation Curator', 'Snack Provider', 'Friendly Neighbour'],
        'Elevada': ['Road Philosopher', 'Storyteller', 'Snack Provider']
    }
    
    obj = dict()
    lst = list()
    pos = 0
    sortkey = ''

    att = ['_id', '_id_company', '_id_driver', '_id_customer', '_id_car', '_origin', '_destination', '_ride_date', '_distance', '_duration', '_amount']

    header = 'Ride'

    des = ['Id', 'Id Company', 'Id Driver', 'Id Customer','Id Car', 'Origin', 'Destination','Ride Date','Distance', 'Duration', 'Amount']
    

    def __init__(self, id, id_company, id_driver, id_customer, id_car, origin, destination, ride_date):
        super().__init__()

        self._id = Ride.get_id(id)

        
        self._id_company = int(id_company)
        self._id_driver = int(id_driver)
        self._id_customer = int(id_customer)
        self._id_car = int(id_car)

        
        if self._id_company not in Company.lst:
            raise ValueError(f"Company {self._id_company} not found")

        if self._id_driver not in Driver.lst:
            raise ValueError(f"Driver {self._id_driver} not found")

        if self._id_customer not in Customer.lst:
            raise ValueError(f"Customer {self._id_customer} not found")

        if self._id_car not in Car.lst:
            raise ValueError(f"Car {self._id_car} not found")

        
        try:
            self._ride_date = datetime.datetime.strptime(ride_date, "%d/%m/%Y").date()
        except:
            self._ride_date = datetime.date.today()
        
        self._origin = origin
        self._destination = destination
        self._distance, self._duration = get_distance_and_time(self._origin, self._destination)
        self._amount = self.calculate_amount()

        
        Ride.obj[self._id] = self
        Ride.lst.append(self._id)

    
    def calculate_amount(self):
        return round(0.8 * self._distance + 0.2 * self._duration + 1, 2)

    @property
    def id(self):
        return self._id

    @property
    def id_driver(self):
        return self._id_driver

    @property
    def id_customer(self):
        return self._id_customer

    @property
    def id_company(self):
        return self._id_company

    @property
    def id_car(self):
        return self._id_car

    @property
    def origin(self):
        return self._origin
    @origin.setter
    def origin(self, origin):
        self._origin = origin

    @property
    def destination(self):
        return self._destination
    @destination.setter
    def destination(self, destination):
        self._destination = destination

    @property
    def ride_date(self):
        return self._ride_date.strftime("%d/%m/%Y")
    @ride_date.setter
    def ride_date(self, ride_date):
        self._ride_date = datetime.datetime.strptime(ride_date, "%d/%m/%Y").date()
        
    @property
    def distance(self):
        return self._distance

    @property
    def duration(self):
        return self._duration

    @property
    def amount(self):
        return self._amount

    
    def estado_da_viagem(self):
        hoje = datetime.date.today()
        return "Concluída" if self._ride_date < hoje else "Por concluir"

