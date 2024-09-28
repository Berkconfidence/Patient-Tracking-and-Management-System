from flask import Flask, render_template, jsonify, request
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import random
from datetime import datetime

class patient(db.Model, UserMixin):
    patientID = db.Column(db.String(15), primary_key=True)
    name = db.Column(db.String(150))
    surname = db.Column(db.String(150))
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)
    gender = db.Column(db.String(10))

class doctor(db.Model, UserMixin):
    doctorID = db.Column(db.String(15), primary_key=True)
    name = db.Column(db.String(150))
    surname = db.Column(db.String(150))
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)
    specialty = db.Column(db.String(150))

class appointment(db.Model, UserMixin):
    randevuID = db.Column(db.Integer, primary_key=True)
    doctorID = db.Column(db.String(15), db.ForeignKey('doctor.doctorID'), nullable=False)
    patientID = db.Column(db.String(15), db.ForeignKey('patient.patientID'), nullable=False)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)
    hour = db.Column(db.Integer)

    files = db.relationship('FileUpload', backref='appointment', lazy='joined')

class FileUpload(db.Model):
    fileID = db.Column(db.Integer, primary_key=True)
    randevuID = db.Column(db.Integer, db.ForeignKey('appointment.randevuID'), nullable=False)
    file_path = db.Column(db.String(300), nullable=False)
    upload_date = db.Column(db.DateTime(timezone=True), default=func.now())
    

def assign_working_hours():
    available_hours = list(range(8, 18))
    working_hours = random.sample(available_hours, 4)
    return sorted(working_hours)

def generate_weekly_schedule(doctor_id):
    schedule = {}
    today = datetime.today()
    for i in range(7): 
        date = today.replace(day=today.day + i)
        schedule[date.strftime('%Y-%m-%d')] = assign_working_hours()
    return schedule

def get_appointment_status(doctor_id, date, hour):
    appointment_record = appointment.query.filter_by(
        doctorID=doctor_id,
        year=date.year,
        month=date.month,
        day=date.day,
        hour=hour
    ).first()

    if appointment_record:
        return 'Dolu'
    elif hour in generate_weekly_schedule(doctor_id)[date.strftime('%Y-%m-%d')]:
        return 'Açık'
    else:
        return 'Kapalı'
    