import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from os import path, makedirs
import os

db = SQLAlchemy()
DB_NAME = "database.db"

# Dosya yükleme klasörü ve izin verilen uzantılar
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Klasör yoksa oluştur
if not os.path.exists(UPLOAD_FOLDER):
    makedirs(UPLOAD_FOLDER)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'berk confidence'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    db.init_app(app)
    migrate = Migrate(app, db)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    create_database(app)

    with app.app_context():
        # JSON verilerini veritabanına yükleme
        load_json_to_db_doctor(r'C:\Code VS\Patient Tracking and Management System\random_doctor.json')
        load_json_to_db(r'C:\Code VS\Patient Tracking and Management System\random_people.json')

    return app

def create_database(app):
    """Veritabanı yoksa oluşturur"""
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()

def load_json_to_db(json_file):
    """Hasta verilerini JSON'dan veritabanına yükler"""
    from .models import patient
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for record in data:
            existing_patient = patient.query.filter_by(patientID=record['patientID']).first()
            if existing_patient:
                continue 

            new_patient = patient(
                patientID=record['patientID'],
                name=record['name'],
                surname=record['surname'],
                year=record['year'],
                month=record['month'],
                day=record['day'],
                gender=record['gender'],
            )
            db.session.add(new_patient)
        db.session.commit()

def load_json_to_db_doctor(json_file):
    """Doktor verilerini JSON'dan veritabanına yükler"""
    from .models import doctor
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for record in data:
            existing_doctor = doctor.query.filter_by(doctorID=record['doctorID']).first()
            if existing_doctor:
                continue

            new_doctor = doctor(
                doctorID=record['doctorID'],
                name=record['name'],
                surname=record['surname'],
                year=record['year'],
                month=record['month'],
                day=record['day'],
                specialty=record['specialty'],
            )
            db.session.add(new_doctor)
        db.session.commit()

def allowed_file(filename):
    """Dosya uzantısını kontrol eder"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
