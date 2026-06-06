from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from classes.company import Company
from classes.driver import Driver
from classes.customer import Customer
from classes.car import Car
from classes.contract import Contract
from classes.ride import Ride
from classes.userlogin import Userlogin
from data.datafile import filename
from datetime import datetime
from datetime import date
import os
from werkzeug.utils import secure_filename


# ================================================================
#  APP CONFIG
# ================================================================
app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ================================================================
#  LOAD DATABASE
# ================================================================
Company.read(filename + 'g13_ridesharing.db')
Driver.read(filename + 'g13_ridesharing.db')
Customer.read(filename + 'g13_ridesharing.db')
Car.read(filename + 'g13_ridesharing.db')
Contract.read(filename + 'g13_ridesharing.db')
Ride.read(filename + 'g13_ridesharing.db')
Userlogin.read(filename + 'g13_ridesharing.db')


# ================================================================
#  CONTEXT PROCESSOR
# ================================================================
@app.context_processor
def inject_user():
    return {"user": session.get("user")}


# ================================================================
#  ADMIN LOGS  (usado pelas routes de admin)
# ================================================================
admin_logs = []

def log_action(action):
    from datetime import datetime

    global admin_logs

    admin_logs.insert(0, {
        "action": action,
        "time": datetime.now().strftime("%H:%M:%S")
    })

    admin_logs = admin_logs[:10]


# ================================================================
#  TABLES (CRUD genérico)
# ================================================================
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

    if session.get("profile_done") != True:
        return redirect(url_for("create_profile"))

    if table not in CLASSES:
        return "<h1>Invalid table</h1>"

    cls = CLASSES[table]

    butshow = "enabled"
    butedit = "disabled"

    option = request.args.get("option")

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


# ================================================================
#  AUTH  —  login, logout, signup, create profile
# ================================================================

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

        if role == "admin":
            return redirect(url_for("admin_dashboard"))

        group_id = Userlogin.get_group_id(user)

        if group_id is None:
            session["profile_done"] = False
            return redirect(url_for("create_profile"))
        else:
            session["profile_done"] = True
            return redirect(url_for("main"))

    return render_template("login.html", resul=resul)


@app.route("/logoff")
def logoff():
    session.clear()
    return redirect(url_for("login"))


@app.route("/signup")
def signup():
    session["profile_done"] = False
    return render_template("signup.html", resul="")


@app.route("/chksignup", methods=["POST"])
def chksignup():
    user = request.form["user"]
    password = request.form["password"]
    role = request.form["role"]

    if len(Userlogin.find(user, '_user')) > 0:
        return render_template("signup.html", resul="User already exists")

    session["temp_user"] = user
    session["temp_password"] = Userlogin.set_password(password)
    session["temp_role"] = role

    return redirect(url_for("create_profile"))


@app.route("/create_profile")
def create_profile():
    role = session.get("role")

    if role is None:
        role = session.get("temp_role")

    if role == "company":
        return render_template("create_company.html")
    elif role == "driver":
        return render_template("create_driver.html")
    elif role == "customer":
        return render_template("create_customer.html")

    return redirect(url_for("login"))


@app.route("/save_customer", methods=["POST"])
def save_customer():
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    dob_str = request.form["date_of_birth"]

    if not name or not email or not phone or not dob_str:
        return render_template("create_customer.html", resul="Preencha todos os campos.")

    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return render_template("create_customer.html", resul="Data inválida.")

    import sqlite3
    conn = sqlite3.connect(filename + 'g13_ridesharing.db')
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(id) FROM Customer")
    result = cursor.fetchone()[0]
    new_id = 1 if result is None else result + 1

    conn.close()

    try:
        obj = Customer(new_id, name, email, phone, dob)
        Customer.insert(obj.id)

        user = session["temp_user"]
        password = session["temp_password"]
        role = session["temp_role"]

        obj_user = Userlogin(0, user, role, password, obj.id)
        Userlogin.insert(obj_user.id)

        session["user"] = user
        session["role"] = role

        session.pop("temp_user", None)
        session.pop("temp_password", None)
        session.pop("temp_role", None)

    except Exception as e:
        print("ERRO CUSTOMER:", e)
        return render_template("create_customer.html", resul="Erro ao criar conta.")

    session["profile_done"] = True
    return redirect(url_for("main", success=1))


@app.route("/save_driver", methods=["POST"])
def save_driver():
    nickname = request.form["nickname"]
    driver_type = request.form["driver_type"]

    if not nickname or not driver_type:
        return render_template("create_driver.html", resul="Preencha todos os campos.")

    import sqlite3
    conn = sqlite3.connect(filename + 'g13_ridesharing.db')
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(id) FROM Driver")
    result = cursor.fetchone()[0]
    new_id = 1 if result is None else result + 1

    conn.close()

    try:
        obj = Driver(new_id, nickname, driver_type, 0)
        Driver.insert(obj.id)

        user = session["temp_user"]
        password = session["temp_password"]
        role = session["temp_role"]

        obj_user = Userlogin(0, user, role, password, obj.id)
        Userlogin.insert(obj_user.id)

        session["user"] = user
        session["role"] = role

        session.pop("temp_user", None)
        session.pop("temp_password", None)
        session.pop("temp_role", None)

    except Exception as e:
        print("ERRO DRIVER:", e)
        return render_template("create_driver.html", resul="Erro ao criar conta.")

    session["profile_done"] = True
    return redirect(url_for("main", success=1))


@app.route("/save_company", methods=["POST"])
def save_company():
    name = request.form["name"]
    begin_date = request.form["begin_date"]

    if not name or not begin_date:
        return render_template("create_company.html", resul="Preencha todos os campos.")

    try:
        begin_date = datetime.strptime(begin_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return render_template("create_company.html", resul="Data inválida!")

    import sqlite3
    conn = sqlite3.connect(filename + 'g13_ridesharing.db')
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(id) FROM Company")
    result = cursor.fetchone()[0]
    new_id = 1 if result is None else result + 1

    conn.close()

    try:
        obj = Company(new_id, name, begin_date)
        Company.insert(obj.id)

        user = session["temp_user"]
        password = session["temp_password"]
        role = session["temp_role"]

        obj_user = Userlogin(0, user, role, password, obj.id)
        Userlogin.insert(obj_user.id)

        session["user"] = user
        session["role"] = role

        session.pop("temp_user", None)
        session.pop("temp_password", None)
        session.pop("temp_role", None)

    except Exception as e:
        print("ERRO COMPANY:", e)
        return render_template("create_company.html", resul="Erro ao criar conta.")

    session["profile_done"] = True
    return redirect(url_for("main", success=1))


# ================================================================
#  SHARED ROUTES  —  main, profile redirect, statistics redirect
# ================================================================

@app.route("/")
def main():
    if session.get("user") is None:
        return redirect(url_for("login"))

    if session.get("profile_done") != True:
        return redirect(url_for("create_profile"))

    role = session.get("role")
    success = request.args.get("success")

    if role == "company":
        return redirect(url_for("company_dashboard"))
    elif role == "customer":
        return render_template("customer_home.html", success=success)
    elif role == "driver":
        return render_template("driver_home.html")

    return redirect(url_for("login"))


@app.route("/profile")
def profile():
    if session.get("user") is None:
        return redirect(url_for("login"))

    role = session.get("role")

    if role == "customer":
        return redirect(url_for("customer_profile"))
    elif role == "driver":
        return redirect(url_for("driver_profile"))
    elif role == "company":
        return redirect(url_for("company_dashboard"))

    return redirect(url_for("main"))


@app.route("/statistics")
def statistics():
    if session.get("user") is None:
        return redirect(url_for("login"))
    role = session.get("role")
    if role == "customer":
        return redirect(url_for("customer_statistics"))
    elif role == "driver":
        return redirect(url_for("driver_statistics"))
    elif role == "company":
        return redirect(url_for("company_dashboard"))
    elif role == "admin":
        return redirect(url_for("admin_dashboard"))
    return redirect(url_for("main"))


# ================================================================
#  SHARED AJAX  —  estimate, rides (confirm, accept, reject, finish, status)
# ================================================================

@app.route("/estimate", methods=["POST"])
def estimate():
    data = request.get_json()
    origin = data.get("origin", "")
    destination = data.get("destination", "")

    if not origin or not destination:
        return jsonify({"success": False, "error": "Missing fields"})

    try:
        from classes.ride import get_distance_and_time
        distance, duration = get_distance_and_time(origin, destination)
        amount = round(0.8 * distance + 0.2 * duration + 1, 2)

        return jsonify({
            "success": True,
            "distance": round(distance, 2),
            "duration": round(duration, 2),
            "amount": amount
        })
    except Exception as e:
        print("ERRO ESTIMATE:", e)
        return jsonify({"success": False, "error": str(e)})


@app.route("/confirm_ride", methods=["POST"])
def confirm_ride():
    if session.get("user") is None:
        return redirect(url_for("login"))

    origin = request.form.get("origin")
    destination = request.form.get("destination")
    phone = request.form.get("phone")
    distance = request.form.get("distance")
    duration = request.form.get("duration")
    amount = request.form.get("amount")
    recommended_driver_id = request.form.get("recommended_driver_id")

    customer_id = Userlogin.get_group_id(session["user"])
    if not customer_id:
        return jsonify({"success": False, "error": "Customer not found"})
    if phone and customer_id in Customer.obj:
        Customer.obj[customer_id]._phone = phone

    company_id = None
    for c in Contract.obj.values():
        if c.is_active:
            company_id = c.id_company
            break

    if company_id is None and len(Company.lst) > 0:
        company_id = Company.lst[0]

    if not company_id:
        return jsonify({"success": False, "error": "No company found"})

    today = datetime.now().strftime("%d/%m/%Y")

    try:
        driver_id = int(recommended_driver_id) if recommended_driver_id and recommended_driver_id != "" else 0
    except (ValueError, TypeError):
        driver_id = 0

    try:
        import sqlite3

        conn = sqlite3.connect(filename + 'g13_ridesharing.db')
        cursor = conn.cursor()

        cursor.execute("SELECT MAX(id) FROM Ride")
        row = cursor.fetchone()
        new_id = 1 if row is None or row[0] is None else row[0] + 1

        new_id = int(new_id)
        company_id_val = int(company_id)
        driver_id_val = int(driver_id)
        customer_id_val = int(customer_id)
        car_id_val = 0

        cursor.execute(
            "INSERT INTO Ride (id, id_company, id_driver, id_customer, id_car, origin, destination, ride_date) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (new_id, company_id_val, driver_id_val, customer_id_val, car_id_val, origin, destination, None)
        )

        conn.commit()
        conn.close()

        new_ride = Ride(new_id, company_id_val, driver_id_val, customer_id_val, 0, origin, destination, None)
        new_ride._distance = float(distance) if distance else 0
        new_ride._duration = float(duration) if duration else 0
        new_ride._amount = float(amount) if amount else 0

        Ride.obj[new_id] = new_ride

        print(f"✅ Viagem criada: ID={new_id}, origin={origin}, destination={destination}, driver_id={driver_id_val}, customer_id={customer_id_val}")

        return jsonify({
            "success": True,
            "ride_id": new_id,
            "message": "Ride created successfully"
        })

    except Exception as e:
        print("ERRO CONFIRM RIDE:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)})


@app.route("/get_ride_status/<int:ride_id>", methods=["GET"])
def get_ride_status(ride_id):
    if session.get("user") is None:
        return jsonify({"success": False, "error": "Not logged in"})

    if ride_id not in Ride.obj:
        return jsonify({"success": False, "error": "Ride not found"})

    ride = Ride.obj[ride_id]

    return jsonify({
        "success": True,
        "ride": {
            "id": ride.id,
            "ride_date": ride.ride_date,
            "driver_id": ride.id_driver
        }
    })


@app.route("/recommend_driver", methods=["POST"])
def recommend_driver():
    if session.get("user") is None:
        return jsonify({"success": False, "error": "Not logged in"})

    data = request.get_json()
    preferences = data.get("preferences", {})

    try:
        recommended_drivers = Ride.selecionar_drivers(preferences)

        if not recommended_drivers:
            return jsonify({"success": False, "error": "No drivers available"})

        best_driver = recommended_drivers[0]

        return jsonify({
            "success": True,
            "driver": {
                "id": best_driver.id,
                "name": best_driver._name if hasattr(best_driver, '_name') else f"Driver {best_driver.id}",
                "driver_type": best_driver.driver_type if hasattr(best_driver, 'driver_type') else "Unknown",
                "rating": round(best_driver.average_ratings(), 1) if hasattr(best_driver, 'average_ratings') else 5.0
            }
        })
    except Exception as e:
        print("ERRO RECOMMEND DRIVER:", e)
        return jsonify({"success": False, "error": str(e)})


@app.route("/accept_ride", methods=["POST"])
def accept_ride():
    if session.get("user") is None:
        return jsonify({"success": False, "error": "Not logged in"})

    data = request.get_json()
    ride_id = data.get("ride_id")

    driver_id = Userlogin.get_group_id(session["user"])

    if driver_id is None or ride_id not in Ride.obj:
        return jsonify({"success": False, "error": "Invalid data"})

    try:
        ride = Ride.obj[ride_id]

        ride._id_driver = driver_id

        today = datetime.now().strftime("%d/%m/%Y")
        ride.ride_date = today

        Ride.update(ride_id)

        return jsonify({"success": True, "message": "Ride accepted"})

    except Exception as e:
        print("ERRO ACCEPT RIDE:", e)
        return jsonify({"success": False, "error": str(e)})


@app.route("/reject_ride", methods=["POST"])
def reject_ride():
    if session.get("user") is None:
        return jsonify({"success": False, "error": "Not logged in"})

    data = request.get_json()
    ride_id = data.get("ride_id")

    if ride_id not in Ride.obj:
        return jsonify({"success": False, "error": "Ride not found"})

    try:
        del Ride.obj[ride_id]

        import sqlite3
        conn = sqlite3.connect(filename + 'g13_ridesharing.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Ride WHERE id = ?", (ride_id,))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Ride rejected and removed"})

    except Exception as e:
        print("ERRO REJECT RIDE:", e)
        return jsonify({"success": False, "error": str(e)})


@app.route("/finish_ride", methods=["POST"])
def finish_ride():
    data = request.get_json()
    ride_id = data.get("ride_id")

    if ride_id not in Ride.obj:
        return jsonify({"success": False, "error": "Ride not found"})

    ride = Ride.obj[ride_id]

    today = datetime.now().strftime("%d/%m/%Y")
    ride.ride_date = today

    Ride.update(ride_id)

    return jsonify({"success": True})


@app.route("/get_driver_rides", methods=["GET"])
def get_driver_rides():
    if session.get("user") is None:
        return jsonify({"success": False, "error": "Not logged in"})

    driver_id = Userlogin.get_group_id(session["user"])
    if driver_id is None:
        return jsonify({"success": False, "error": "Driver not found"})

    try:
        recommended_ride = None

        for ride in Ride.obj.values():
            if ride.id_driver == driver_id and ride._ride_date is None:
                customer_name = Customer.obj[ride.id_customer]._name if ride.id_customer in Customer.obj else "Unknown"

                recommended_ride = {
                    "id": ride.id,
                    "origin": ride.origin,
                    "destination": ride.destination,
                    "distance": ride.formatted_distance,
                    "duration": ride.formatted_duration,
                    "amount": ride.amount or 0,
                    "customer_name": customer_name,
                    "ride_date": ride.ride_date
                }
                break

        pending_rides = []
        for ride in Ride.obj.values():
            if ride.id_driver == 0 and ride._ride_date is None:
                customer_name = Customer.obj[ride.id_customer]._name if ride.id_customer in Customer.obj else "Unknown"

                pending_rides.append({
                    "id": ride.id,
                    "origin": ride.origin,
                    "destination": ride.destination,
                    "distance": ride.formatted_distance,
                    "duration": ride.formatted_duration,
                    "amount": ride.amount or 0,
                    "customer_name": customer_name,
                    "ride_date": ride.ride_date
                })

        return jsonify({
            "success": True,
            "recommended_ride": recommended_ride,
            "pending_rides": pending_rides
        })

    except Exception as e:
        print("ERRO GET DRIVER RIDES:", e)
        return jsonify({"success": False, "error": str(e)})


# ================================================================
#  CUSTOMER
# ================================================================

@app.route("/customer/profile")
def customer_profile():

    if session.get("user") is None:
        return redirect(url_for("login"))

    user = session["user"]
    customer_id = Userlogin.get_group_id(user)

    cliente = Customer.obj.get(customer_id)

    page = request.args.get("page", 1, type=int)
    per_page = 5

    from datetime import datetime

    hoje = datetime.today().date()

    historico = []
    for r in Ride.obj.values():
        if r.id_customer == customer_id and r._ride_date is not None:
            if r._ride_date < hoje:
                historico.append(r)

    historico = sorted(historico, key=lambda r: r._ride_date, reverse=True)

    start = (page - 1) * per_page
    end = start + per_page

    historico_paginated = historico[start:end]

    total = len(historico)
    total_pages = (total + per_page - 1) // per_page

    from datetime import datetime
    idade = None
    if cliente.date_of_birth:
        try:
            dob = datetime.strptime(cliente.date_of_birth, "%d/%m/%Y").date()
            idade = hoje.year - dob.year - ((hoje.month, hoje.day) < (dob.month, dob.day))
        except:
            pass

    return render_template(
        "customer_profile.html",
        cliente=cliente,
        historico=historico_paginated,
        page=page,
        total_pages=total_pages,
        idade=idade
    )


@app.route("/customer/edit", methods=["GET", "POST"])
def customer_edit():
    if session.get("user") is None:
        return redirect(url_for("login"))

    user = session["user"]
    customer_id = Userlogin.get_group_id(user)
    cliente = Customer.obj.get(customer_id)

    if request.method == "POST":
        cliente._name = request.form["name"]
        cliente._email = request.form["email"]
        cliente._phone = request.form["phone"]

        new_dob = request.form.get("date_of_birth")
        if new_dob:
            try:
                from datetime import datetime as dt_parse
                parsed = dt_parse.strptime(new_dob, "%Y-%m-%d")
                cliente.date_of_birth = parsed.strftime("%d/%m/%Y")
            except:
                pass

        remove_photo = request.form.get("remove_photo")
        photo = request.files.get("photo")

        if remove_photo == "true":
            cliente.photo = None
        elif photo and photo.filename:
            import os
            ext = os.path.splitext(photo.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                photo_filename = f"customer_{customer_id}{ext}"
                photo_path = os.path.join("static", "images", "customer", photo_filename)
                os.makedirs(os.path.dirname(photo_path), exist_ok=True)
                photo.save(photo_path)
                cliente.photo = url_for('static', filename=f'images/customer/{photo_filename}')

        Customer.update(cliente.id)

        return redirect(url_for("customer_profile"))

    return render_template("customer_edit.html", cliente=cliente)


@app.route("/customer/statistics")
def customer_statistics():
    if session.get("user") is None or session.get("role") != "customer":
        return redirect(url_for("login"))

    user = session["user"]
    customer_id = Userlogin.get_group_id(user)

    rides = [r for r in Ride.obj.values() if r.id_customer == customer_id and r._ride_date is not None]

    total_rides = len(rides)
    total_spent = sum(r.amount for r in rides if r.amount)
    total_distance = sum(r.distance for r in rides if r.distance)
    total_duration = sum(r.duration for r in rides if r.duration)

    return render_template("customer_statistics.html",
                           total_rides=total_rides,
                           total_spent=round(total_spent, 2),
                           total_distance=round(total_distance, 2),
                           total_duration=round(total_duration, 2))


# ================================================================
#  DRIVER
# ================================================================

@app.route("/driver/profile")
def driver_profile():
    if session.get("user") is None:
        return redirect(url_for("login"))

    user = session["user"]
    driver_id = Userlogin.get_group_id(user)

    driver = Driver.obj.get(driver_id)

    page = request.args.get("page", 1, type=int)
    per_page = 5

    historico = []
    for r in Ride.obj.values():
        if r.id_driver == driver_id and r._ride_date is not None:
            historico.append(r)

    historico = sorted(historico, key=lambda r: r._ride_date if r._ride_date else datetime.min.date(), reverse=True)

    start = (page - 1) * per_page
    end = start + per_page

    historico_paginated = historico[start:end]

    total = len(historico)
    total_pages = (total + per_page - 1) // per_page if per_page else 1
    if total_pages == 0: total_pages = 1

    return render_template(
        "driver_profile.html",
        driver=driver,
        historico=historico_paginated,
        page=page,
        total_pages=total_pages,
        total_rides=total
    )


@app.route("/driver/edit", methods=["GET", "POST"])
def driver_edit():
    if session.get("user") is None:
        return redirect(url_for("login"))

    user = session["user"]
    driver_id = Userlogin.get_group_id(user)
    driver = Driver.obj.get(driver_id)

    if request.method == "POST":
        driver.nickname = request.form["nickname"]
        driver.driver_type = request.form["driver_type"]
        Driver.update(driver.id)
        return redirect(url_for("driver_profile"))

    return render_template("driver_edit.html", driver=driver)


@app.route("/driver/statistics")
def driver_statistics():
    if session.get("user") is None or session.get("role") != "driver":
        return redirect(url_for("login"))

    user = session["user"]
    driver_id = Userlogin.get_group_id(user)

    rides = [r for r in Ride.obj.values() if r.id_driver == driver_id and r._ride_date is not None]

    total_rides = len(rides)
    total_earned = sum(r.amount for r in rides if r.amount)
    total_distance = sum(r.distance for r in rides if r.distance)
    total_duration = sum(r.duration for r in rides if r.duration)

    return render_template("driver_statistics.html",
                           total_rides=total_rides,
                           total_earned=round(total_earned, 2),
                           total_distance=round(total_distance, 2),
                           total_duration=round(total_duration, 2))


# ================================================================
#  COMPANY
# ================================================================

@app.route("/company/dashboard")
def company_dashboard():
    if session.get("user") is None:
        return redirect(url_for("login"))

    if session.get("role") != "company":
        return redirect(url_for("main"))

    user = session["user"]
    company_id = Userlogin.get_group_id(user)
    company = Company.obj.get(company_id)

    from classes.ride import Ride

    all_rides = [r for r in Ride.obj.values() if r.id_company == company_id]

    total_rides = len(all_rides)
    total_revenue = sum([float(r.amount) for r in all_rides if r.amount])

    all_rides.sort(key=lambda r: r._ride_date, reverse=True)
    rides = all_rides[:5]

    profit = company.lucro()

    return render_template(
        "company_dashboard.html",
        company=company,
        total_rides=total_rides,
        total_revenue=round(total_revenue, 2),
        profit=profit,
        rides=rides
    )


@app.route("/company/profile")
def company_profile():

    if session.get("role") != "company":
        return redirect(url_for("login"))

    company_id = Userlogin.get_group_id(session["user"])
    company = Company.obj.get(company_id)

    return render_template(
        "company_profile.html",
        user=session["user"],
        company=company
    )


@app.route("/company/edit", methods=["GET", "POST"])
def edit_company():

    if session.get("role") != "company":
        return redirect(url_for("login"))

    import datetime as dt

    company_id = Userlogin.get_group_id(session["user"])
    company = Company.obj.get(company_id)

    if request.method == "POST":

        new_name = request.form.get("name")
        new_begin_date = request.form.get("begin_date")
        photo = request.files.get("photo")

        if new_name:
            company._name = new_name

        if new_begin_date:
            date = dt.datetime.strptime(new_begin_date, "%Y-%m-%d")
            company.begin_date = date.strftime("%d/%m/%Y")

        remove_photo = request.form.get("remove_photo")
        photo = request.files.get("photo")

        if remove_photo == "true":
            company.photo = None
        elif photo and photo.filename:
            import os
            ext = os.path.splitext(photo.filename)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                photo_filename = f"company_{company_id}{ext}"
                photo_path = os.path.join("static", "images", "company", photo_filename)
                os.makedirs(os.path.dirname(photo_path), exist_ok=True)
                photo.save(photo_path)
                from flask import url_for
                company.photo = url_for('static', filename=f'images/company/{photo_filename}')

        Company.update(company._id)

        return redirect(url_for("company_profile"))

    return render_template(
        "company_edit.html",
        user=session["user"],
        company=company
    )


@app.route("/company/drivers")
def company_drivers():

    if session.get("role") != "company":
        return redirect(url_for("login"))

    company_id = Userlogin.get_group_id(session["user"])

    page_active = request.args.get("page_active", 1, type=int)
    page_available = request.args.get("page", 1, type=int)

    per_page_active = 5
    per_page_available = 5

    active_contracts = [
        c for c in Contract.obj.values()
        if c.id_company == company_id and c.is_active
    ]

    active_drivers = []

    for c in active_contracts:
        d = Driver.obj[c.id_driver]
        d.contract_end = c.contract_end
        active_drivers.append(d)

    active_drivers = sorted(active_drivers, key=lambda d: d.id)

    start_a = (page_active - 1) * per_page_active
    end_a = start_a + per_page_active
    active_paginated = active_drivers[start_a:end_a]

    total_active = len(active_drivers)
    total_pages_active = (total_active + per_page_active - 1) // per_page_active

    all_drivers = sorted(Driver.obj.values(), key=lambda d: d.id)

    available_drivers = [
        d for d in all_drivers
        if not any(
            c.id_driver == d.id and c.id_company == company_id and c.is_active
            for c in Contract.obj.values()
        )
    ]

    start = (page_available - 1) * per_page_available
    end = start + per_page_available

    available_paginated = available_drivers[start:end]

    total_available = len(available_drivers)
    total_pages = (total_available + per_page_available - 1) // per_page_available

    return render_template(
        "company_drivers.html",
        active_drivers=active_paginated,
        available_drivers=available_paginated,
        page=page_available,
        total_pages=total_pages,
        page_active=page_active,
        total_pages_active=total_pages_active
    )


@app.route("/company/cars", methods=["GET", "POST"])
def company_cars():
    add = request.args.get("add")
    if session.get("role") != "company":
        return redirect(url_for("login"))

    from classes.car import Car

    company_id = Userlogin.get_group_id(session["user"])

    action = request.args.get("action")
    car_id = request.args.get("id")
    edit_id = request.args.get("edit")
    show_id = request.args.get("show")

    if action == "delete" and car_id:
        car_id = int(car_id)

        import sqlite3
        from data.datafile import filename

        conn = sqlite3.connect(filename + 'g13_ridesharing.db')
        cursor = conn.cursor()

        cursor.execute("DELETE FROM Car WHERE id = ?", (car_id,))

        conn.commit()
        conn.close()

        if car_id in Car.obj:
            del Car.obj[car_id]
            Car.lst.remove(car_id)

        return redirect(url_for("company_cars"))

    if request.method == "POST":
        car_id = int(request.form["id"])
        description = request.form["description"]
        car_type = int(request.form["car_type"])

        import sqlite3
        from data.datafile import filename

        conn = sqlite3.connect(filename + 'g13_ridesharing.db')
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE Car SET description = ?, car_type = ? WHERE id = ?",
            (description, car_type, car_id)
        )

        conn.commit()
        conn.close()

        car = Car.obj.get(car_id)
        if car:
            car.description = description
            car.car_type = car_type

        return redirect(url_for("company_cars"))

    cars = [c for c in Car.obj.values() if c.id_company == company_id]

    return render_template(
        "company_cars.html",
        cars=cars,
        edit_id=edit_id,
        show_id=show_id,
        add=add
    )


@app.route("/add_car", methods=["POST"])
def add_car():

    if session.get("role") != "company":
        return redirect(url_for("login"))

    import sqlite3
    from data.datafile import filename
    from classes.car import Car

    company_id = Userlogin.get_group_id(session["user"])

    description = request.form["description"]
    car_type = int(request.form["car_type"])

    conn = sqlite3.connect(filename + 'g13_ridesharing.db')
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(id) FROM Car")
    result = cursor.fetchone()[0]
    new_id = 1 if result is None else result + 1

    cursor.execute(
        "INSERT INTO Car (id, description, id_company, car_type) VALUES (?, ?, ?, ?)",
        (new_id, description, company_id, car_type)
    )

    conn.commit()
    conn.close()

    new_car = Car(new_id, description, company_id, car_type)
    Car.obj[new_car.id] = new_car
    Car.lst.append(new_car.id)

    return redirect(url_for("company_cars"))


@app.route("/hire_driver/<int:driver_id>", methods=["POST"])
def hire_driver(driver_id):

    if session.get("role") != "company":
        return redirect(url_for("login"))

    company_id = Userlogin.get_group_id(session["user"])

    start = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    permanent = request.form.get("permanent")

    if permanent == "true":
        end = None
    else:
        new_date_str = request.form.get("contract_end")

        if new_date_str:
            end = datetime.strptime(new_date_str, "%Y-%m-%dT%H:%M").strftime("%d/%m/%Y %H:%M:%S")
        else:
            end = None

    contract = Contract(0, start, end, company_id, driver_id)

    Contract.insert(contract.id)

    return redirect(url_for("company_drivers"))


@app.route("/fire_driver/<int:driver_id>")
def fire_driver(driver_id):

    if session.get("role") != "company":
        return redirect(url_for("login"))

    company_id = Userlogin.get_group_id(session["user"])

    for c in Contract.obj.values():
        if c.id_company == company_id and c.id_driver == driver_id and c.is_active:
            c.terminate()
            Contract.update(c.id)
            break

    return redirect(url_for("company_drivers"))


@app.route("/renew_driver/<int:driver_id>", methods=["POST"])
def renew_driver(driver_id):

    if session.get("role") != "company":
        return redirect(url_for("login"))

    company_id = Userlogin.get_group_id(session["user"])

    permanent = request.form.get("permanent")

    for c in Contract.obj.values():
        if c.id_company == company_id and c.id_driver == driver_id and c.is_active:

            if permanent == "true":
                c.contract_end = None
            else:
                new_date_str = request.form.get("new_date")

                try:
                    new_date = datetime.strptime(new_date_str, "%Y-%m-%dT%H:%M")
                except:
                    return "Invalid date format"

                c.contract_end = new_date

            Contract.update(c.id)
            break

    return redirect(url_for("company_drivers"))


# ================================================================
#  ADMIN
# ================================================================

@app.route("/admin/dashboard")
def admin_dashboard():

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    from classes.car import Car
    from classes.company import Company
    from classes.userlogin import Userlogin
    from classes.ride import Ride
    from classes.contract import Contract
    from classes.driver import Driver
    from classes.customer import Customer

    import matplotlib
    matplotlib.use('Agg')

    import matplotlib.pyplot as plt

    import pandas as pd
    import io
    import base64

    total_users = len(Userlogin.obj)
    total_companies = len(Company.lst)
    total_cars = len(Car.obj)
    total_rides = len(Ride.obj)
    total_contracts = len(Contract.obj)

    total_customers = len(Customer.obj)
    total_drivers = len(Driver.obj)

    data = {
        'Type': ['Customers', 'Drivers', 'Companies'],
        'Count': [
            total_customers,
            total_drivers,
            total_companies
        ]
    }

    df = pd.DataFrame(data)

    plt.figure(figsize=(6, 4))

    colors = ['#00ff88', '#00bfff', '#ffaa00']

    bars = plt.bar(df['Type'], df['Count'], color=colors)

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height,
                f'{int(height)}',
                ha='center', va='bottom')

    plt.xlabel("Type")
    plt.ylabel("Count")

    plt.grid(axis='y', linestyle='--', alpha=0.4)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)

    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return render_template(
        "admin_dashboard.html",
        user=session["user"],

        total_rides=total_rides,
        total_cars=total_cars,
        total_contracts=total_contracts,

        total_customers=total_customers,
        total_drivers=total_drivers,
        total_companies=total_companies,

        plot_url=plot_url,
    )


@app.route("/admin/profile")
def admin_profile():

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    from classes.userlogin import Userlogin

    user = session["user"]
    user_id = Userlogin.get_user_id(user)
    admin = Userlogin.obj[user_id]

    log_action("Accessed profile")

    return render_template(
        "admin_profile.html",
        user=user,
        admin=admin,
        total_users=len(Userlogin.obj),
        logs=admin_logs
    )


@app.route("/admin/edit_profile", methods=["POST"])
def edit_admin_profile():

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    from classes.userlogin import Userlogin

    user = session["user"]
    user_id = Userlogin.get_user_id(user)
    admin = Userlogin.obj[user_id]

    new_username = request.form.get("username")
    new_password = request.form.get("password")

    if new_username:
        admin._user = new_username
        session["user"] = new_username

    if new_password:
        admin._password = Userlogin.set_password(new_password)

    admin.update(admin.id)

    log_action("Updated profile")

    return redirect(url_for("admin_profile"))


@app.route("/admin/manage_users")
def admin_users():

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    from classes.userlogin import Userlogin
    from classes.customer import Customer
    from classes.company import Company
    from classes.driver import Driver

    users = []

    roles = {}
    details = {}

    for u, user_obj in Userlogin.obj.items():

        group = str(user_obj.usergroup).lower().strip()

        if group == "admin":
            continue

        ref_id = user_obj.id_usergroup

        users.append(u)
        roles[u] = group

    for u in users:

        user_obj = Userlogin.obj[u]

        group = str(user_obj.usergroup).lower().strip()
        ref_id = user_obj.id_usergroup
        roles[u] = group

        if group == "customer":

            cust = Customer.obj.get(ref_id)

            if cust:
                details[u] = {
                    "group": "customer",
                    "name": cust.name,
                    "email": cust.email,
                    "phone": cust.phone,
                    "dob": cust.date_of_birth
                }
            else:
                details[u] = {"group": "customer"}

        elif group == "company":

            comp = Company.obj.get(ref_id)

            if comp:
                details[u] = {
                    "group": "company",
                    "name": comp.name,
                    "begin": comp.begin_date
                }
            else:
                details[u] = {"group": "company"}

        elif group == "driver":

            drv = Driver.obj.get(ref_id)

            if drv:
                details[u] = {
                    "group": "driver",
                    "nickname": drv.nickname,
                    "type": drv.driver_type,
                    "rating": round(drv.average_ratings(), 2)
                }
            else:
                details[u] = {"group": "driver"}

    return render_template(
        "admin_manage_users.html",
        users=users,
        roles=roles,
        details=details,
        user=session["user"]
    )


@app.route("/admin/edit_user/<user>", methods=["POST"])
def edit_user(user):
    #Não edita username, password nem role, só os dados do perfil. Para mudar password/role tem de apagar e criar outro user.

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    from classes.userlogin import Userlogin
    from classes.customer import Customer
    from classes.company import Company
    from classes.driver import Driver

    user_id = int(user)
    user_obj = Userlogin.obj.get(user_id)

    group = user_obj.usergroup
    ref_id = user_obj.id_usergroup

    if group == "customer":
        obj = Customer.obj.get(ref_id)

        obj.name = request.form["name"]
        obj.email = request.form["email"]
        obj.phone = request.form["phone"]
        obj.date_of_birth = request.form["dob"]

        obj.update(obj.id)

    elif group == "company":
        obj = Company.obj.get(ref_id)

        obj.name = request.form["name"]
        obj.begin_date = request.form["begin"]
        print("ANTES UPDATE:", obj.name)
        obj.update(obj.id)
        print("DEPOIS UPDATE:", obj.name)

    elif group == "driver":
        obj = Driver.obj.get(ref_id)

        obj.nickname = request.form["nickname"]
        obj.driver_type = request.form["type"]

        obj.update(obj.id)

    log_action(f"✏️ Edited {user}")

    return redirect(url_for("admin_users"))


@app.route("/admin/delete_user/<user>")
def delete_user(user):
    #Não elimina o objeto da conta, apenas elimina o userlogin e o acesso. O objeto "driver"/"customer"/"company" fica lá, mas sem userlogin associado, logo sem acesso.

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    from classes.userlogin import Userlogin
    import sqlite3

    user_id = int(user)

    if user_id in Userlogin.obj:
        del Userlogin.obj[user_id]

    if user_id in Userlogin.lst:
        Userlogin.lst.remove(user_id)

    log_action(f"Deleted user {user}")

    conn = sqlite3.connect(Userlogin.db_path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Users WHERE id = ?", (user_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("admin_users"))


@app.route("/admin/user_details/<user>")
def user_details(user):

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    from classes.userlogin import Userlogin

    if user not in Userlogin.obj:
        return redirect(url_for("admin_users"))

    user_obj = Userlogin.obj[user]

    return render_template(
        "admin_user_details.html",
        user=user,
        role=user_obj._usergroup
    )


@app.route("/admin/get_warnings")
def get_warnings():

    if session.get("role") != "admin":
        return jsonify({"error": "unauthorized"}), 403

    from classes.ride import Ride

    illegal = Ride.get_illegal_rides()

    return jsonify({
        "count": len(illegal),
        "data": illegal[:5]
    })


@app.route("/admin/top_users")
def admin_top_users():

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    return render_template(
        "admin_top_users.html",
        user=session["user"]
    )


@app.route("/admin/get_top/<group>/<metric>")
def get_top(group, metric):

    from classes.ride import Ride
    from classes.driver import Driver
    from classes.customer import Customer
    from classes.company import Company
    from classes.contract import Contract
    from classes.car import Car
    from flask import jsonify

    result = []

    customer_stats = {}

    if group == "customers":
        for r in Ride.obj.values():

            cid = r.id_customer

            if cid not in customer_stats:
                customer_stats[cid] = {"rides": 0, "distance": 0, "amount": 0}

            customer_stats[cid]["rides"] += 1
            customer_stats[cid]["distance"] += r._distance or 0
            customer_stats[cid]["amount"] += r._amount or 0

    driver_stats = {}

    if group == "drivers":
        for r in Ride.obj.values():

            did = r.id_driver

            if did not in driver_stats:
                driver_stats[did] = {"rides": 0, "distance": 0, "amount": 0}

            driver_stats[did]["rides"] += 1
            driver_stats[did]["distance"] += r._distance or 0
            driver_stats[did]["amount"] += r._amount or 0

    contracts_by_driver = {}
    contracts_by_company = {}

    if metric in ["contracts", "drivers", "rating"] or group == "companies":

        for c in Contract.obj.values():
            contracts_by_driver.setdefault(c.id_driver, []).append(c)
            contracts_by_company.setdefault(c.id_company, []).append(c)

    cars_by_company = {}

    if metric == "cars":
        for car in Car.obj.values():
            cars_by_company.setdefault(car.id_company, []).append(car)

    if group == "drivers":

        for d in Driver.obj.values():

            stats = driver_stats.get(d.id, {})
            contracts = contracts_by_driver.get(d.id, [])

            if metric == "rides":
                value = stats.get("rides", 0)

            elif metric == "distance":
                value = stats.get("distance", 0)

            elif metric == "amount":
                value = stats.get("amount", 0)

            elif metric == "contracts":
                value = len(contracts)

            elif metric == "rating":
                value = d.average_ratings()

            else:
                value = 0

            driver_name = getattr(d, "nickname", None) or getattr(d, "name", None) or f"Driver {d.id}"

            name = f"Driver {d.id}"
            subtitle = driver_name

            result.append({
                "name": name,
                "subtitle": subtitle,
                "value": round(value, 2)
            })

    elif group == "customers":

        for c in Customer.obj.values():

            stats = customer_stats.get(c.id, {})

            if metric == "rides":
                value = stats.get("rides", 0)

            elif metric == "distance":
                value = stats.get("distance", 0)

            elif metric == "amount":
                value = stats.get("amount", 0)

            else:
                value = 0

            customer_name = getattr(c, "name", None) or f"Customer {c.id}"

            name = f"Customer {c.id}"
            subtitle = customer_name

            result.append({
                "name": name,
                "subtitle": subtitle,
                "value": round(value, 2)
            })

    elif group == "companies":

        for comp in Company.obj.values():

            contracts = contracts_by_company.get(comp.id, [])

            if metric == "drivers":
                value = len(set(c.id_driver for c in contracts))

            elif metric == "cars":
                value = len(cars_by_company.get(comp.id, []))

            elif metric == "contracts":
                value = len(contracts)

            elif metric == "profit":
                value = comp.lucro()

            elif metric == "rating":

                driver_ids = set(c.id_driver for c in contracts)

                ratings = [
                    d.average_ratings()
                    for d in Driver.obj.values()
                    if d.id in driver_ids
                ]

                value = sum(ratings)/len(ratings) if ratings else 0

            else:
                value = 0

            company_name = getattr(comp, "name", None) or f"Company {comp.id}"

            name = f"Company {comp.id}"
            subtitle = company_name

            result.append({
                "name": name,
                "subtitle": subtitle,
                "value": round(value, 2)
            })

    result.sort(key=lambda x: (-x["value"], x["name"]))

    return jsonify(result[:3])


@app.route("/admin/get_company_lucro/<user>")
def get_company_lucro(user):

    if session.get("role") != "admin":
        return {"lucro": 0}

    from classes.company import Company

    for comp_id, comp in Company.obj.items():

        if str(comp_id) == str(user):
            return {"lucro": comp.lucro()}

    return {"lucro": 0}


# ================================================================
#  RUN
# ================================================================
if __name__ == '__main__':
    app.run(debug=True)