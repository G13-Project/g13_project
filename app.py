from flask import Flask, render_template, request, session, redirect, url_for
from classes.company import Company
from classes.driver import Driver
from classes.customer import Customer
from classes.car import Car
from classes.contract import Contract
from classes.ride import Ride
from classes.userlogin import Userlogin
from data.datafile import filename

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'

# ---------------- LOAD DATABASE ----------------
Company.read(filename + 'g13_ridesharing.db')
Driver.read(filename + 'g13_ridesharing.db')
Customer.read(filename + 'g13_ridesharing.db')
Car.read(filename + 'g13_ridesharing.db')
Contract.read(filename + 'g13_ridesharing.db')
Ride.read(filename + 'g13_ridesharing.db')
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
    role = request.form["role"]

    resul = Userlogin.chk_password(user, password)

    if resul == "Valid":
        session["user"] = user
        session["role"] = role
        return redirect(url_for("main"))

    return render_template("login.html", resul=resul)

# ---------------- SIGNUP ----------------
@app.route("/signup")
def signup():
    return render_template("signup.html", resul="")

@app.route("/chksignup", methods=["POST"])
def chksignup():
    user = request.form["user"]
    password = request.form["password"]
    role = request.form["role"]

    # verificar se já existe
    if len(Userlogin.find(user, 'user')) > 0:
        return render_template("signup.html", resul="User already exists")

    # criar user
    obj = Userlogin(0, user, role, Userlogin.set_password(password))

    # guardar na BD
    Userlogin.insert(obj.id)

    return redirect(url_for("login"))

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

    return redirect(url_for("index", table="company"))

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

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)
