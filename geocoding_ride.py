from data.datafile import filename
from classes.ride import Ride
from geocoding_db import find_geocoding
import sqlite3


#foi corrido uma vez para adicionar as colunas vazias
#import sqlite3
#from data.datafile import filename

#conn = sqlite3.connect(filename + 'g13_ridesharing.db')
#cursor = conn.cursor()

#cursor.execute("ALTER TABLE Ride ADD COLUMN distance REAL")
#cursor.execute("ALTER TABLE Ride ADD COLUMN duration REAL")
#cursor.execute("ALTER TABLE Ride ADD COLUMN amount REAL")

#conn.commit()
#conn.close()

#print("Colunas adicionadas")


# ✅ carregar rides
Ride.read(filename + 'g13_ridesharing.db')

conn = sqlite3.connect(filename + 'g13_ridesharing.db')
cursor = conn.cursor()

count = 0

for r in Ride.obj.values():

    origin = r.origin
    destination = r.destination

    if not origin or not destination:
        continue

    try:
        # ✅ vai buscar da tabela geocoding
        result = find_geocoding(origin, destination)

        if result:
            dist, dur, amount = result

            # ✅ atualiza BD diretamente
            cursor.execute("""
                UPDATE Ride
                SET distance = ?, duration = ?, amount = ?
                WHERE id = ?
            """, (dist, dur, amount, r.id))

            count += 1
            print(f"✅ Ride {r.id} updated")

        else:
            print(f"⚠️ Sem geocoding: {origin} → {destination}")

    except Exception as e:
        print(f"❌ Erro ride {r.id}:", e)

conn.commit()
conn.close()

print(f"\n✅ {count} rides atualizadas")