from classes.company import Company
from classes.driver import Driver
from classes.customer import Customer
from classes.userlogin import Userlogin
from data.datafile import filename

import random
import string
import sqlite3

def limpar_users():
    conn = sqlite3.connect(filename + 'g13_ridesharing.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Users") 
    conn.commit()
    conn.close()
    
    Userlogin.obj = {}
    Userlogin.lst = []

    print("Users antigos apagados")


# ---------------- LOAD DATABASE ----------------
Company.read(filename + 'g13_ridesharing.db')
Driver.read(filename + 'g13_ridesharing.db')
Customer.read(filename + 'g13_ridesharing.db')
Userlogin.read(filename + 'g13_ridesharing.db')




# ---------------- PASSWORD GENERATOR ----------------
def gerar_password(tamanho=8):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(tamanho))


# ---------------- GUARDAR PASSWORDS ----------------
def guardar_passwords(nome, passwords):
    with open("passwords.txt", "a", encoding="utf-8") as f:
        f.write(f"\n--- {nome} ---\n")
        for user, pwd in passwords.items():
            f.write(f"{user} -> {pwd}\n")


# ---------------- CRIAR USERS ----------------
def criar_users():

    print("A criar customers...")
    passwords_c = {}

    for c in Customer.obj.values():
        username = c.email.lower()

        pwd = gerar_password()
        hashed = Userlogin.set_password(pwd)

        uid = Userlogin.get_user_id(username)

        if uid == 0:
            u = Userlogin(0, username, "customer", hashed, c.id)
            Userlogin.insert(u.id)
        else:
            obj = Userlogin.obj[uid]
            obj.password = hashed
            obj._id_usergroup = c.id   
            Userlogin.update(uid)

        passwords_c[username] = pwd

    guardar_passwords("CUSTOMERS", passwords_c)


    print("A criar companies...")
    passwords_comp = {}

    for comp in Company.obj.values():
        username = (
            comp.name.lower()
            .replace(" ", "_")
            .replace(",", "")
            + "_" + str(comp.id)
        )

        pwd = gerar_password()
        hashed = Userlogin.set_password(pwd)

        uid = Userlogin.get_user_id(username)

        if uid == 0:
            u = Userlogin(0, username, "company", hashed, comp.id)
            Userlogin.insert(u.id)
        else:
            obj = Userlogin.obj[uid]
            obj.password = hashed
            obj._id_usergroup = comp.id
            Userlogin.update(uid)

        passwords_comp[username] = pwd

    guardar_passwords("COMPANIES", passwords_comp)


    print("A criar drivers...")
    passwords_d = {}

    for d in Driver.obj.values():
        username = (
            d.nickname.lower().replace(" ", "_")
            + "_" + str(d.id)
        )

        pwd = gerar_password()
        hashed = Userlogin.set_password(pwd)

        uid = Userlogin.get_user_id(username)

        if uid == 0:
            u = Userlogin(0, username, "driver", hashed, d.id)
            Userlogin.insert(u.id)
        else:
            obj = Userlogin.obj[uid]
            obj.password = hashed
            obj._id_usergroup = d.id
            Userlogin.update(uid)

        passwords_d[username] = pwd

    guardar_passwords("DRIVERS", passwords_d)


    # -------- ADMIN --------
    print("A criar admin...")

    admin_user = "Itiji"
    pwd = "acbritogoat"
    hashed = Userlogin.set_password(pwd)

    uid = Userlogin.get_user_id(admin_user)

    if uid == 0:
        u = Userlogin(0, admin_user, "admin", hashed, None) 
        Userlogin.insert(u.id)
        print(f"Admin criado: {admin_user} -> {pwd}")
    else:
        obj = Userlogin.obj[uid]
        obj.password = hashed
        obj._id_usergroup = None
        Userlogin.update(uid)
        print(f"Admin atualizado: {admin_user} -> {pwd}")

    print("Tudo feito!")


# ---------------- RUN ----------------
#Este código demora cerca de 5 minutos a correr devido ao 
#elevado número de objetos na base de dados, sendo que foi
#apenas necessário corrê-lo uma vez no inicio para a criação
#de uma conta para todos os dados iniciais.

#Para simular essa primeira vez que foi preciso correr,
# o método limpar_users() limpa da base de dados os users existentes
#para ser depois possivel gerar users para todos os objetos sem se
#correr em erros de "sqlite3.IntegrityError: UNIQUE constraint failed: Users.id"

if __name__ == '__main__':

    # limpar ficheiro sempre
    open("passwords.txt", "w").close()

    limpar_users()
    criar_users()