from flask import Flask, render_template, request, session, redirect, url_for
from classes.company import Company
from classes.driver import Driver
from classes.customer import Customer
from classes.car import Car
from classes.contract import Contract
from classes.ride import Ride
from data.datafile import filename

app = Flask(__name__)

# Load all data
Company.read(filename + 'g13_ridesharing.db')
Driver.read(filename + 'g13_ridesharing.db')
Customer.read(filename + 'g13_ridesharing.db')
Car.read(filename + 'g13_ridesharing.db')
Contract.read(filename + 'g13_ridesharing.db')
Ride.read(filename + 'g13_ridesharing.db')

prev_option = ""
app.secret_key = 'BAD_SECRET_KEY'

# Dictionary to map class names to class objects
CLASSES = {
    'company': Company,
    'driver': Driver,
    'customer': Customer,
    'car': Car,
    'contract': Contract,
    'ride': Ride
}

def get_class_attributes(cls):
    """Get attributes configuration for a class"""
    return {
        'att': cls.att,
        'des': cls.des,
        'header': cls.header
    }

def get_form_data(cls, form):
    """Extract form data based on class attributes"""
    data = {}
    for attr in cls.att:
        attr_name = attr[1:]  # Remove underscore prefix
        if attr_name in form:
            data[attr_name] = form[attr_name]
    return data

def build_object_string(cls, form):
    """Build object string from form data"""
    parts = []
    for attr in cls.att:
        attr_name = attr[1:]
        if attr_name in form:
            parts.append(form[attr_name])
    return ';'.join(parts)

@app.route("/")
def main():
    return redirect(url_for('index', table='company'))

@app.route("/<table>", methods=["post","get"])
def index(table):
    global prev_option
    
    if table not in CLASSES:
        return "<h1>Invalid table</h1>", 404
    
    cls = CLASSES[table]
    attrs = get_class_attributes(cls)
    
    butshow, butedit = "enabled", "disabled"
    option = request.args.get("option")
    
    if option == "edit":
        butshow, butedit = "disabled", "enabled"
    elif option == "delete":
        obj = cls.current()
        cls.remove(obj.id)
        if not cls.previous():
            cls.first()
    elif option == "insert":
        butshow, butedit = "disabled", "enabled"
    elif option == 'cancel':
        pass
    elif prev_option == 'insert' and option == 'save':
        strobj = str(cls.get_id(0))
        form_data = get_form_data(cls, request.form)
        for key, value in form_data.items():
            strobj += ';' + value
        obj = cls.from_string(strobj)
        cls.insert(obj.id)
        cls.last()
    elif prev_option == 'edit' and option == 'save':
        obj = cls.current()
        for attr, desc in zip(cls.att, attrs['des']):
            attr_name = attr[1:]
            if attr_name.lower() in request.form:
                setattr(obj, attr, request.form[attr_name.lower()])
        cls.update(obj.id)
    elif option == "first":
        cls.first()
    elif option == "previous":
        cls.previous()
    elif option == "next":
        cls.nextrec()
    elif option == "last":
        cls.last()
    elif option == 'exit':
        return "<h1>Thank you for using this app</h1>"
    
    prev_option = option
    
    # Get current object
    if len(cls.lst) == 0 or (option == 'insert' or option == 'cancel'):
        obj = None
        form_values = {attr[1:]: "" for attr in cls.att}
    else:
        obj = cls.current()
        form_values = {attr[1:]: getattr(obj, attr) for attr in cls.att}
    
    return render_template("index.html", 
                    table=table,
                    tables=list(CLASSES.keys()),
                    butshow=butshow, 
                    butedit=butedit,
                    header=attrs['header'],
                    attributes=attrs['des'],
                    form_values=form_values)
        
if __name__ == '__main__':
    app.run(debug=True)