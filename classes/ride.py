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

    # Falha se faltar origem ou destino
    if not origin_str or not destination_str:
        return 0, 0

    key = (origin_str, destination_str)

    # Verificar cache
    if key in Ride.distance_cache:
        return Ride.distance_cache[key]

    try:
        origin = geocode(origin_str)
        destination = geocode(destination_str)

        # Geocode falhou → fallback
        if origin is None or destination is None:
            print("Geocode falhou:", origin_str, "→", destination_str)
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

        # Validar valores
        if distance_km <= 0 or duration_min <= 0 or distance_km > 1000:
            result = fallback_distance_time(origin_str, destination_str)
        else:
            result = (round(distance_km, 2), round(duration_min, 2))

        # Guardar na cache
        Ride.distance_cache[key] = result
        Ride.distance_cache[(destination_str, origin_str)] = result

        return result

    except Exception as e:
        print("Erro na API:", e)

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
        'Animado': ['Vibe setter', 'Playlist Maestro', 'Snack Provider']
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

    # Attribute names list, identifier attribute must be the first one and callled 'id' 
    att = ['_id', '_id_company', '_id_driver', '_id_customer', '_id_car', '_origin', '_destination', '_ride_date', '_distance', '_duration', '_amount', '_status']
    # Class header title 
    header = 'Ride'
    # Field description for use in, for example, input form 
    des = ['Id', 'Id Company', 'Id Driver', 'Id Customer','Id Car', 'Origin', 'Destination','Ride Date','Distance', 'Duration', 'Amount', 'Status']
    

    def __init__(self, id, id_company, id_driver, id_customer, id_car, origin, destination, ride_date, distance=None, duration=None, amount=None, status='PENDING'):
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

        # Status deve ser: 'PENDING', 'ACTIVE', 'FINISHED', ou 'REJECTED'
        status_upper = status.upper() if isinstance(status, str) else 'PENDING'
        self._status = status_upper if status_upper in ['PENDING', 'ACTIVE', 'FINISHED', 'REJECTED'] else 'PENDING'
        
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

    # Properties

    @property
    def id(self):
        return self._id
    # Id não tem setter porque a sua mudança causaria problemas para encontrar o objeto

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
    def status(self):
        return self._status
    
    @status.setter
    def status(self, status):
        status_upper = status.upper() if isinstance(status, str) else 'PENDING'
        if status_upper in ['PENDING', 'ACTIVE', 'FINISHED', 'REJECTED']:
            self._status = status_upper
        else:
            self._status = 'PENDING'    
    
    @property
    def distance(self):
        if self._distance is None:
            self.calcular_viagem()
        return self._distance

    # Formatar distância para formatos como 5,43 km, 12,7 km, 107 km
    @property
    def formatted_distance(self):
        if not self._distance:
            return "0 km"
        
        dist = float(self._distance)
        if dist >= 100:
            return f"{int(round(dist))} km"
        elif dist >= 10:
            return f"{round(dist, 1)} km"
        else:
            return f"{round(dist, 2)} km"


    @property
    def duration(self):
        if self._duration is None:
            self.calcular_viagem()
        return self._duration

    # Formatar duração para formatos como 5,43 min --> 5 min, 107 min --> 1h 47min
    @property
    def formatted_duration(self):
        if not self._duration:
            return "0 min"
        
        total_minutes = int(round(float(self._duration)))
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        if hours > 0:
            if minutes > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{hours}h"
        else:
            return f"{minutes} min"

    @property
    def amount(self):
        if self._amount is None:
            self.calcular_viagem()
        return self._amount

    def calcular_viagem(self):

        if self._distance is None or self._duration is None:

            try:
                # 1. Procurar na BD
                result = find_geocoding(self._origin, self._destination)

                if result:
                    self._distance, self._duration, self._amount = result
                    return

                # 2. Se não existir → calcular
                print("A calcular:", self._origin, "→", self._destination)

                self._distance, self._duration = get_distance_and_time(
                    self._origin, self._destination
                )

                self._amount = self.calculate_amount()

                # 3. Guardar na tabela Geocoding
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

            # 4. Guardar também na Ride
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

            # 3. Score de preferências (PESO: 60%)
            driver_type = driver.driver_type
            preferences_matched = driver_types_desejados.count(driver_type)

            if preferences_matched > 0:
                # 4. Rating médio com confidence factor (PESO: 40%)
                rating_avg = driver.average_ratings()
                num_reviews = len(driver._ratings) if hasattr(driver, '_ratings') else 0
                
                # Confidence factor: penaliza drivers com poucas reviews
                # Com 5+ reviews, confidence = 1.0
                # Com 0 reviews, confidence = 0 (rating não contribui)
                confidence_factor = min(num_reviews / 5.0, 1.0)

                # 5. Pontuação ponderada com nova fórmula
                # - Preferências: 60% da pontuação (mais importante)
                # - Rating: 40% da pontuação (ajustado por confidence factor)
                preferences_norm = preferences_matched / 3.0  # máximo 3
                rating_norm = (rating_avg / 5.0) if rating_avg > 0 else 0.0  # normaliza 0-1
                
                pontuacao = (preferences_norm * 0.6) + (rating_norm * confidence_factor * 0.4)

                resultados.append((driver, pontuacao, num_reviews))

        # 6. Ordenar pela pontuação final
        resultados.sort(key=lambda x: x[1], reverse=True)

        # Retornar drivers com metadados de reviews
        drivers_with_metadata = []
        for driver, score, num_reviews in resultados:
            drivers_with_metadata.append({
                'driver': driver,
                'score': score,
                'num_reviews': num_reviews
            })
        
        return drivers_with_metadata
    
    @staticmethod
    def get_rides_by_customer(id_customer):
        return [r for r in Ride.obj.values() if r.id_customer == id_customer]
    
    @staticmethod
    def get_rides_by_driver(id_driver):
        return [r for r in Ride.obj.values() if r.id_driver == id_driver]

    @classmethod
    def insert(cls, code):
        import sqlite3
        from data.datafile import filename

        if code not in cls.obj:
            return

        ride = cls.obj[code]

        conn = sqlite3.connect(filename + 'g13_ridesharing.db')
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO Ride (id, id_company, id_driver, id_customer, id_car, origin, destination, ride_date, distance, duration, amount, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (ride.id, ride.id_company, ride.id_driver, ride.id_customer, ride.id_car, ride.origin, ride.destination, ride.ride_date, ride.distance, ride.duration, ride.amount, ride.status)
        )

        conn.commit()
        conn.close()

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
                amount = ?,
                status = ?     
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
            ride._status,
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

                # Contrato permanente
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

    # Para o aviso
    @staticmethod
    def count_illegal_rides():
        return len(Ride.get_illegal_rides())