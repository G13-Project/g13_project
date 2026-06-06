from classes.company import Company
from classes.driver import Driver
from classes.customer import Customer
from classes.car import Car
from classes.gclass import Gclass
from geocoding_db import find_geocoding, insert_geocoding

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

    # ✅ evitar erros básicos
    if not origin_str or not destination_str:
        return 0, 0

    key = (origin_str, destination_str)

    # ✅ 1. verificar cache
    if key in Ride.distance_cache:
        return Ride.distance_cache[key]

    try:
        origin = geocode(origin_str)
        destination = geocode(destination_str)

        # ✅ geocode falhou → fallback
        if origin is None or destination is None:
            print("⚠️ Geocode falhou:", origin_str, "→", destination_str)
            result = fallback_distance_time(origin_str, destination_str)

            Ride.distance_cache[key] = result
            Ride.distance_cache[(destination_str, origin_str)] = result

            return result

        url = f"http://router.project-osrm.org/route/v1/driving/{origin};{destination}?overview=false"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if "routes" not in data or not data["routes"]:
            result = fallback_distance_time(origin_str, destination_str)

            Ride.distance_cache[key] = result
            Ride.distance_cache[(destination_str, origin_str)] = result

            return result

        route = data["routes"][0]

        distance_km = route["distance"] / 1000
        duration_min = route["duration"] / 60

        # ✅ validar valores
        if distance_km <= 0 or duration_min <= 0 or distance_km > 1000:
            result = fallback_distance_time(origin_str, destination_str)
        else:
            result = (round(distance_km, 2), round(duration_min, 2))

        # ✅ guardar no cache
        Ride.distance_cache[key] = result
        Ride.distance_cache[(destination_str, origin_str)] = result

        return result

    except Exception as e:
        print("⚠️ Erro na API:", e)

        result = fallback_distance_time(origin_str, destination_str)

        Ride.distance_cache[key] = result
        Ride.distance_cache[(destination_str, origin_str)] = result

        return result



class Ride(Gclass):
    distance_cache = {}
 
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
    

    def __init__(self, id, id_company, id_driver, id_customer, id_car, origin, destination, ride_date, distance=None, duration=None, amount=None):
        super().__init__()

        self._id = Ride.get_id(id)

        
        self._id_company = int(id_company)
        self._id_driver = int(id_driver)
        self._id_customer = int(id_customer)
        self._id_car = int(id_car) if id_car else 0

        
        # Permitir empresas que podem não estar carregadas em memória
        # if self._id_company not in Company.lst:
        #     raise ValueError(f"Company {self._id_company} not found")

        # Permitir id_driver = 0 (driver não atribuído) e drivers que podem não estar carregados
        # if self._id_driver != 0 and self._id_driver not in Driver.lst:
        #     raise ValueError(f"Driver {self._id_driver} not found")

        # Customer pode não estar carregado em memória mas está na BD
        # if self._id_customer not in Customer.lst:
        #     raise ValueError(f"Customer {self._id_customer} not found")

        # Permitir id_car = 0 (carro não atribuído)
        # if self._id_car != 0 and self._id_car not in Car.lst:
        #     raise ValueError(f"Car {self._id_car} not found")

        if ride_date in (None, "", "None"):
            self._ride_date = None
        else:
            try:
                self._ride_date = datetime.datetime.strptime(ride_date, "%d/%m/%Y").date()
            except:
                self._ride_date = None

   
        
        self._origin = origin
        self._destination = destination
        
        
        self._distance = float(distance) if distance not in (None, "", "None") else None
        self._duration = float(duration) if duration not in (None, "", "None") else None
        self._amount = float(amount) if amount not in (None, "", "None") else None

        Ride.obj[self._id] = self
        Ride.lst.append(self._id)
 
        if self._distance is None or self._duration is None:
            self.calcular_viagem()

        
        
    def calculate_amount(self):
        if self._distance is None or self._duration is None:
            return 0
        return round(0.8 * float(self._distance) + 0.2 * float(self._duration) + 1, 2)


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
        if self._ride_date is None:
            return None
        return self._ride_date.strftime("%d/%m/%Y")
    @ride_date.setter
    def ride_date(self, ride_date):
        if ride_date in (None, "", "None"):
            self._ride_date = None
        else:
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



    
    def calcular_viagem(self):

        if self._distance is None or self._duration is None:

            try:
                #1. procurar na BD
                result = find_geocoding(self._origin, self._destination)

                if result:
                    #print("✅ Usou BD:", self._origin, "→", self._destination)

                    self._distance, self._duration, self._amount = result
                    return

                #2. se não existir → calcular
                print("⚠️ A calcular:", self._origin, "→", self._destination)

                self._distance, self._duration = get_distance_and_time(
                    self._origin, self._destination
                )

                self._amount = self.calculate_amount()

                #3. guardar na tabela Geocoding
                insert_geocoding(
                    self._origin,
                    self._destination,
                    self._distance,
                    self._duration,
                    self._amount
                )
            except Exception as e:
                print(f"ERRO calcular_viagem: {e}")
                # Valores por defeito se falhar
                self._distance = 0
                self._duration = 0
                self._amount = 0

            #4. guardar também na Ride
            Ride.update(self.id)
    
    def estado_da_viagem(self):
        # Se ainda não tem data → viagem pendente
        if self._ride_date is None:
            return "Pending"

        hoje = datetime.date.today()

        # Se a data da viagem é anterior a hoje → concluída
        return "Concluded" if self._ride_date < hoje else "To be concluded"


    @staticmethod
    def selecionar_drivers(preferencias: dict, id_company=None):
        from classes.contract import Contract
        categorias = {
            "Velocidade": Ride.Velocidade,
            "Segurança": Ride.Segurança,
            "Horário": Ride.Horário,
            "Tecnologia": Ride.Tecnologia,
            "Ambiente": Ride.Ambiente,
            "Interacao": Ride.Interacao
            }

        # 1. Converter preferências para driver types
        driver_types_desejados = []

        for categoria, escolha in preferencias.items():
            if categoria in categorias and escolha in categorias[categoria]:
                driver_types_desejados.extend(categorias[categoria][escolha])

        resultados = []

        # 2. Percorrer contratos ativos
        for contract_id in Contract.lst:
            contract = Contract.obj[contract_id]

            if not contract.is_active:
                continue

            if id_company is not None and contract.id_company != id_company:
                continue

            driver = Driver.obj[contract.id_driver]

            # 3. Score de preferências
            driver_type = driver.driver_type
            score = driver_types_desejados.count(driver_type)

            if score > 0:
                # 4. Rating médio
                rating = driver.average_ratings()

                # 5. Pontuação ponderada (2/3 para score e 1/3 para rating)
                score_norm = score / 3
                rating_norm = rating / 5

                pontuacao = (2 * score_norm + rating_norm) / 3

                resultados.append((driver, pontuacao))

        # 6. Ordenar pela pontuação final
        resultados.sort(key=lambda x: x[1], reverse=True)

        return [driver for driver, _ in resultados]
    @staticmethod
    def get_rides_by_customer(id_customer):
        return [r for r in Ride.obj.values() if r.id_customer == id_customer]
    @staticmethod
    def get_rides_by_driver(id_driver):
        return [r for r in Ride.obj.values() if r.id_driver == id_driver]

 


    @staticmethod
    def update(id):
        import sqlite3
        from data.datafile import filename

        if id not in Ride.obj:
            return

        ride = Ride.obj[id]

        conn = sqlite3.connect(filename + 'g13_ridesharing.db')
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Ride
            SET 
                id_company = ?,
                id_driver = ?,
                id_customer = ?,
                id_car = ?,
                origin = ?,
                destination = ?,
                ride_date = ?,
                distance = ?,     
                duration = ?,     
                amount = ?        
            WHERE id = ?
        """, (
            ride._id_company,
            ride._id_driver,
            ride._id_customer,
            ride._id_car,
            ride._origin,
            ride._destination,
            ride._ride_date.strftime("%d/%m/%Y") if ride._ride_date else None,
            ride._distance,
            ride._duration,
            ride._amount,
            ride._id
        ))

        conn.commit()
        conn.close()

   
    
    @staticmethod
    def get_illegal_rides():
        from classes.contract import Contract

        illegal = []

        for ride in Ride.obj.values():

            if ride.id_driver == 0 or ride._ride_date is None:
                continue

            contracts = [
                c for c in Contract.obj.values()
                if c.id_driver == ride.id_driver
            ]

            valid = False

            for c in contracts:

                begin = c._contract_start.date()
                end = c._contract_end.date() if c._contract_end else None

                # ✅ contrato permanente
                if end is None:
                    if ride._ride_date >= begin:
                        valid = True
                        break
                else:
                    if begin <= ride._ride_date <= end:
                        valid = True
                        break

            if not valid and contracts:
                c = contracts[0]

                illegal.append({
                    "driver_id": ride.id_driver,
                    "ride_date": ride._ride_date.strftime("%d/%m/%y"),
                    "contract": (
                        f"{c._contract_start.strftime('%d/%m/%y')} - "
                        + ("Permanent" if c._contract_end is None else c._contract_end.strftime('%d/%m/%y'))
                    )
                })

        return illegal


    @staticmethod #para o aviso
    def count_illegal_rides():
        return len(Ride.get_illegal_rides())

