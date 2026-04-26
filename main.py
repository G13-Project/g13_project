import os
import sys

# Define o caminho para a pasta raiz e para a pasta classes
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
pasta_classes = os.path.join(diretorio_atual, 'classes')

#evita o ModuleNotFoundError
sys.path.append(diretorio_atual)
sys.path.append(pasta_classes)


from classes.company import Company
from classes.driver import Driver
from classes.customer import Customer
from classes.car import Car
from classes.contract import Contract
from classes.ride import Ride

# Define o caminho para a base de dados na pasta 'data'
caminho_base = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(caminho_base, 'data', 'g13_ridesharing.db')

def iniciar():
    print("--- A carregar base de dados ---")
    try:
        # Ordem de leitura para evitar erros de IDs não encontrados
        Company.read(db_path)
        
        Driver.read(db_path)
        Customer.read(db_path)
        Car.read(db_path)
        Contract.read(db_path)
        Ride.read(db_path)
        print("Dados carregados!")
        return True
    except Exception as e:
        print(f"Erro ao carregar: {e}")
        return False


if iniciar():
    
    test_class = Company  #for example, it can be any class that I want to test
    
    op = ''
    while op != 'q':
        p = test_class.current()
        print(f'\n--- TESTE INDIVIDUAL: {test_class.header} ---')
        
        if p:
            print(f'Dados na Memória: {p}')
        else:
            print("A lista está vazia! Verifica se a tabela 'Company' tem dados no SQLite.")

        print('l-Listar Tudo | n-Próximo | p-Anterior | q-Sair')
        op = input(' Escolha uma opção: ').lower()
        
        if op == 'l':
            for code in test_class.lst: 
                print(test_class.obj[code])
        elif op == 'n': test_class.nextrec()
        elif op == 'p': test_class.previous()