import sqlite3
from data.datafile import filename

DB = filename + 'g13_ridesharing.db'

def create_table():

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Geocoding (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origin TEXT,
            destination TEXT,
            distance REAL,
            duration REAL,
            amount REAL
        )
    """)

    conn.commit()
    conn.close()

    print("✅ Tabela Geocoding criada (ou já existia)")


def find_geocoding(origin, destination):

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "SELECT distance, duration, amount FROM Geocoding WHERE origin=? AND destination=?",
        (origin, destination)
    )

    row = cur.fetchone()

    #tentar inverso
    if not row:
        cur.execute(
            "SELECT distance, duration, amount FROM Geocoding WHERE origin=? AND destination=?",
            (destination, origin)
        )
        row = cur.fetchone()

    conn.close()

    return row  # None ou (distance, duration, amount)


#inserir
def insert_geocoding(origin, destination, distance, duration, amount):

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    #evitar duplicado
    cur.execute(
        "SELECT id FROM Geocoding WHERE origin=? AND destination=?",
        (origin, destination)
    )

    if cur.fetchone():
        conn.close()
        return

    cur.execute(
        """
        INSERT INTO Geocoding (origin, destination, distance, duration, amount)
        VALUES (?, ?, ?, ?, ?)
        """,
        (origin, destination, distance, duration, amount)
    )

    conn.commit()
    conn.close()

#executar para criar a tabela "Geocoding" na BD (apenas foi necessario correr uma vez no início)
if __name__ == "__main__":
    create_table()
