from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///safety.db'
db = SQLAlchemy(app)

# ------------------ DATABASE MODELS ------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(15))
    password = db.Column(db.String(200))

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(15))

class SOS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    latitude = db.Column(db.String(50))
    longitude = db.Column(db.String(50))
    time = db.Column(db.DateTime, default=datetime.utcnow)

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    location = db.Column(db.String(200))
    description = db.Column(db.Text)
    time = db.Column(db.DateTime, default=datetime.utcnow)

# ------------------ ROUTES ------------------

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        hashed_password = generate_password_hash(request.form['password'])
        new_user = User(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template("register.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            return redirect('/dashboard')
    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template("dashboard.html")
    return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# -------- CONTACTS --------

@app.route('/contacts', methods=['GET','POST'])
def contacts():
    if request.method == 'POST':
        contact = Contact(
            user_id=session['user_id'],
            name=request.form['name'],
            phone=request.form['phone']
        )
        db.session.add(contact)
        db.session.commit()
    user_contacts = Contact.query.filter_by(user_id=session['user_id']).all()
    return render_template("contacts.html", contacts=user_contacts)

# -------- SOS --------

@app.route('/sos', methods=['GET','POST'])
def sos():
    if request.method == 'POST':
        alert = SOS(
            user_id=session['user_id'],
            latitude=request.form['latitude'],
            longitude=request.form['longitude']
        )
        db.session.add(alert)
        db.session.commit()
        return "SOS Alert Sent Successfully!"
    return render_template("sos.html")

# -------- REPORT INCIDENT --------

@app.route('/report', methods=['GET','POST'])
def report():
    if request.method == 'POST':
        incident = Incident(
            user_id=session['user_id'],
            location=request.form['location'],
            description=request.form['description']
        )
        db.session.add(incident)
        db.session.commit()
        return redirect('/dashboard')
    return render_template("report.html")

# -------- VIEW ALERTS --------

@app.route('/alerts')
def alerts():
    user_alerts = SOS.query.filter_by(user_id=session['user_id']).all()
    return render_template("alerts.html", alerts=user_alerts)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
