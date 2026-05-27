from flask import Flask, render_template, request, session, redirect, url_for
from classes.company import Company
from classes.driver import Driver
from classes.customer import Customer
from classes.car import Car
from classes.contract import Contract
from classes.ride import Ride
from classes.userlogin import Userlogin
from data.datafile import filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'

# ---------------- LOAD DATABASE ----------------
Company.read(filename + 'g13_ridesharing.db')
Driver.read(filename + 'g13_ridesharing.db')
Customer.read(filename + 'g13_ridesharing.db')
Car.read(filename + 'g13_ridesharing.db')
Contract.read(filename + 'g13_ridesharing.db')
#Ride.read(filename + 'g13_ridesharing.db')
Userlogin.read(filename + 'g13_ridesharing.db')

# ---------------- USER IN TEMPLATES ----------------
@app.context_processor
def inject_user():
    return {"user": session.get("user")}

# ---------------- LOGIN ----------------
@app.route("/login")
def login():
    return render_template("login.html", resul="")

@app.route("/chklogin", methods=["POST"])
def chklogin():
    user = request.form["user"]
    password = request.form["password"]

    resul = Userlogin.chk_password(user, password)

    if resul == "Valid":
        role = Userlogin.get_role(user)

        session["user"] = user
        session["role"] = role

        session["profile_done"] = False  # 🔴 IMPORTANTE

        return redirect(url_for("create_profile"))

    return render_template("login.html", resul=resul)

@app.route("/create_profile")
def create_profile():
    role = session.get("role")

    if role == "company":
        return render_template("create_company.html")
    elif role == "driver":
        return render_template("create_driver.html")
    elif role == "customer":
        return render_template("create_customer.html")



# ---------------- SIGNUP ----------------
@app.route("/signup")
def signup():
    session["profile_done"] = False
    return render_template("signup.html", resul="")

@app.route("/chksignup", methods=["POST"])
def chksignup():
    user = request.form["user"]
    password = request.form["password"]
    role = request.form["role"]

    if len(Userlogin.find(user, 'user')) > 0:
        return render_template("signup.html", resul="User already exists")

    obj = Userlogin(0, user, role, Userlogin.set_password(password))
    Userlogin.insert(obj.id)

    # ✅ LOGIN AUTOMÁTICO
    session["user"] = user
    session["role"] = role

    # ✅ vai direto para formulário
    return redirect(url_for("create_profile"))




@app.route("/save_customer", methods=["POST"])
def save_customer():
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    dob_str = request.form["date_of_birth"]

    # ✅ validar campos vazios
    if not name or not email or not phone or not dob_str:
        return render_template(
            "create_customer.html",
            resul="Preencha todos os campos."
        )

    # ✅ converter data
    from datetime import datetime
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return render_template(
            "create_customer.html",
            resul="Data inválida."
        )

    # ✅ GERAR ID SEGURO (IMPORTANTE 🔥)
    if len(Customer.lst) == 0:
        new_id = 1
    else:
        new_id = max(Customer.lst) + 1

    try:
        obj = Customer(new_id, name, email, phone, dob)
        Customer.insert(obj.id)
    except Exception as e:
        print("ERRO CUSTOMER:", e)
        return render_template(
            "create_customer.html",
            resul="Erro ao criar conta."
        )

    session["profile_done"] = True
    return redirect(url_for("main", success=1))



@app.route("/save_driver", methods=["POST"])
def save_driver():
    nickname = request.form["nickname"]
    driver_type = request.form["driver_type"]

    # ✅ valida campos vazios
    if not nickname or not driver_type:
        return render_template(
            "create_driver.html",
            resul="Preencha todos os campos."
        )

    # ✅ calcular ID seguro
    if len(Driver.lst) == 0:
        new_id = 1
    else:
        new_id = max(Driver.lst) + 1

    try:
        obj = Driver(new_id, nickname, driver_type, 0)
        Driver.insert(obj.id)
    except Exception as e:
        print("ERRO DRIVER:", e)
        return render_template(
            "create_driver.html",
            resul="Erro ao criar conta."
        )

    session["profile_done"] = True
    return redirect(url_for("main", success=1))

@app.route("/save_company", methods=["POST"])
def save_company():
    name = request.form["name"]
    begin_date = request.form["begin_date"]


    if not name or not begin_date:
        return render_template(
            "create_company.html",
            resul="Preencha todos os campos."
        )

    try:
        # ✅ converter de YYYY-MM-DD → DD/MM/YYYY
        begin_date = datetime.strptime(begin_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return render_template(
            "create_company.html",
            resul="Data inválida!"
        )


    obj = Company(0, name, begin_date)

    



    session["profile_done"] = True
    return redirect(url_for("main", success=1))



# ---------------- LOGOUT ----------------
@app.route("/logoff")
def logoff():
    session.clear()
    return redirect(url_for("login"))

# ---------------- MAIN ----------------
@app.route("/")
def main():
    if session.get("user") is None:
        return redirect(url_for("login"))

    # 🔴 NOVO — impedir voltar ao form depois de completar
    if session.get("profile_done") != True:
        return redirect(url_for("create_profile"))

    success = request.args.get("success")

    return render_template("index.html", success=success)

# ---------------- TABLES ----------------
CLASSES = {
    'company': Company,
    'driver': Driver,
    'customer': Customer,
    'car': Car,
    'contract': Contract,
    'ride': Ride
}

prev_option = ""

@app.route("/<table>", methods=["GET", "POST"])
def index(table):
    global prev_option

    if session.get("user") is None:
        return redirect(url_for("login"))
    

    # obrigar a preencher perfil primeiro
    if session.get("profile_done") != True:
        return redirect(url_for("create_profile"))


    if table not in CLASSES:
        return "<h1>Invalid table</h1>"

    cls = CLASSES[table]

    butshow = "enabled"
    butedit = "disabled"

    option = request.args.get("option")

    # --------- AÇÕES ---------
    if option == "edit":
        butshow = "disabled"
        butedit = "enabled"

    elif option == "cancel":
        pass

    elif prev_option == "edit" and option == "save":
        obj = cls.current()
        for attr in cls.att:
            name = attr[1:]
            if name in request.form:
                setattr(obj, attr, request.form[name])
        cls.update(obj.id)

    elif option == "first":
        cls.first()

    elif option == "previous":
        cls.previous()

    elif option == "next":
        cls.nextrec()

    elif option == "last":
        cls.last()

    elif option == "exit":
        return redirect(url_for("main"))

    prev_option = option

    # --------- VALORES DO FORM ---------
    if len(cls.lst) == 0:
        form_values = {}
    else:
        obj = cls.current()
        form_values = {attr[1:]: getattr(obj, attr) for attr in cls.att}

    return render_template(
        "index.html",
        table=table,
        tables=list(CLASSES.keys()),
        butshow=butshow,
        butedit=butedit,
        form_values=form_values
    )
@app.route("/perfil_cliente")
def perfil_cliente():
        return render_template("perfil_cliente.html")

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)
