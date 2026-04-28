import os
import sys
import sqlite3

# ---------------- PATHS ---------------- #

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLASSES_DIR = os.path.join(BASE_DIR, 'classes')

sys.path.append(BASE_DIR)
sys.path.append(CLASSES_DIR)

from classes.company import Company
from classes.driver import Driver
from classes.customer import Customer
from classes.car import Car
from classes.contract import Contract
from classes.ride import Ride

DB_PATH = os.path.join(BASE_DIR, 'data', 'g13_ridesharing.db')

# ---------------- DB ---------------- #

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def get_columns(table):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f'PRAGMA table_info({table})')
    cols = [row[1] for row in cur.fetchall() if row[1] != 'id']
    conn.close()
    return cols

# ---------------- LOAD ---------------- #

def iniciar():
    print('--- A carregar base de dados ---')
    try:
        Company.read(DB_PATH)
        Driver.read(DB_PATH)
        Customer.read(DB_PATH)
        Car.read(DB_PATH)
        Contract.read(DB_PATH)
        Ride.read(DB_PATH)
        print('Dados carregados!')
        return True
    except Exception as e:
        print(f'Erro ao carregar: {e}')
        return False

# ---------------- MENU ---------------- #

def menu_teste(test_class):

    table = test_class.__name__
    columns = get_columns(table)
    op = ''

    while op != 'q':

        atual = test_class.current()
        print(f'\n--- TESTE INDIVIDUAL: {table} ---')
        print(f'Atual: {atual}' if atual else 'Lista vazia.')

        print('''
l - Listar tudo
n - Próximo
p - Anterior
b - Buscar por ID
a - Acrescentar
u - Alterar
e - Eliminar
q - Sair
''')

        op = input('Opção: ').lower().strip()

        # LISTAR
        if op == 'l':
            for k in test_class.lst:
                print(test_class.obj[k])

        # NAVEGAÇÃO
        elif op == 'n':
            test_class.nextrec()

        elif op == 'p':
            test_class.previous()

        # BUSCAR
        elif op == 'b':
            try:
                bid = int(input('ID a procurar: '))
            except ValueError:
                print('ID inválido!')
                continue

            if bid in test_class.obj:
                print('Encontrado:')
                print(test_class.obj[bid])
            else:
                print('ID não existe!')

        # ACRESCENTAR
        elif op == 'a':
            try:
                new_id = int(input('Novo ID: '))
            except ValueError:
                print('ID inválido!')
                continue

            if new_id in test_class.obj:
                print('ID já existe!')
                continue

            values = []
            for col in columns:
                val = input(f'{col}: ').strip()
                values.append(val if val != '' else None)

            try:
                conn = get_connection()
                cur = conn.cursor()

                sql = f'''
                    INSERT INTO {table} (id,{",".join(columns)})
                    VALUES ({",".join(["?"]*(len(columns)+1))})
                '''
                cur.execute(sql, [new_id] + values)
                conn.commit()
                conn.close()

                test_class(new_id, *values)
                print('Registo acrescentado (DB + memória).')

            except sqlite3.IntegrityError:
                print('Erro de integridade (ID duplicado ou FK inválida).')

            except sqlite3.OperationalError:
                print('Base de dados ocupada. Fecha o DB Browser.')

        # ALTERAR
        elif op == 'u':
            try:
                uid = int(input('ID a alterar: '))
            except ValueError:
                print('ID inválido!')
                continue

            if uid not in test_class.obj:
                print('ID não existe!')
                continue

            obj = test_class.obj[uid]
            novos = []

            for col in columns:
                atual_val = getattr(obj, col)
                val = input(f'{col} [{atual_val}] (ENTER mantém): ').strip()
                novos.append(atual_val if val == '' else val)

            try:
                conn = get_connection()
                cur = conn.cursor()

                sets = ', '.join([f'{c}=?' for c in columns])
                cur.execute(
                    f'UPDATE {table} SET {sets} WHERE id=?',
                    novos + [uid]
                )
                conn.commit()
                conn.close()

                for col, val in zip(columns, novos):
                    setattr(obj, col, val)

                print('Registo atualizado (DB + memória).')

            except sqlite3.IntegrityError:
                print('Erro de integridade.')

            except sqlite3.OperationalError:
                print('Base de dados ocupada.')

        # ELIMINAR
        elif op == 'e':
            try:
                did = int(input('ID a eliminar: '))
            except ValueError:
                print('ID inválido!')
                continue

            if did not in test_class.obj:
                print('ID não existe!')
                continue

            if input('Tem a certeza que quer eliminar? (s/n): ').lower() != 's':
                continue

            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(f'DELETE FROM {table} WHERE id=?', (did,))
                conn.commit()
                conn.close()

                del test_class.obj[did]
                test_class.lst.remove(did)

                print('Registo eliminado (DB + memória).')

            except sqlite3.IntegrityError:
                print('Não é possível eliminar: registo em uso.')

# ---------------- MAIN ---------------- #

if iniciar():

    print('''
Escolhe a classe:
1 - Company
2 - Driver
3 - Customer
4 - Car
5 - Contract
6 - Ride
''')

    classes = {
        '1': Company,
        '2': Driver,
        '3': Customer,
        '4': Car,
        '5': Contract,
        '6': Ride
    }

    escolha = input('Opção: ').strip()

    if escolha in classes:
        menu_teste(classes[escolha])
    else:
        print('Opção inválida!')