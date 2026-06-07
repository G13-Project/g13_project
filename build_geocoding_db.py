from data.datafile import filename
from classes.company import Company
from classes.driver import Driver
from classes.customer import Customer
from classes.car import Car
from classes.contract import Contract
from classes.ride import Ride
from geocoding_db import insert_geocoding
from classes.ride import get_distance_and_time


Company.read(filename + 'g13_ridesharing.db')
Driver.read(filename + 'g13_ridesharing.db')
Customer.read(filename + 'g13_ridesharing.db')
Car.read(filename + 'g13_ridesharing.db')
Contract.read(filename + 'g13_ridesharing.db')
Ride.read(filename + 'g13_ridesharing.db')


def build_geocoding_table():

    count = 0

    for r in Ride.obj.values():

        origin = r.origin
        destination = r.destination

        if not origin or not destination:
            continue

        try:
            #calcula só uma vez por par
            dist, dur = get_distance_and_time(origin, destination)

            amount = round(0.8 * dist + 0.2 * dur + 1, 2)

            #guarda na BD
            insert_geocoding(origin, destination, dist, dur, amount)
            print(f"✅ Inserido: {origin} → {destination}")
            count += 1

        except Exception as e:
            print(f"❌ Erro na ride {r.id}:", e)

    print(f"✅ {count} entradas processadas")


if __name__ == "__main__":
    build_geocoding_table()
