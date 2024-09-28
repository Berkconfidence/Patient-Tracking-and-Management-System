from flask import Blueprint, render_template, request, flash, jsonify
from .models import patient, doctor, appointment
from . import db

auth = Blueprint('auth',__name__)

@auth.route('/patient-login',methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        tckimlik = request.form.get('tc-kimlik')
        year = request.form.get('year')
        month = request.form.get('month')
        day = request.form.get('day') 

        patient1 = patient.query.filter_by(patientID=tckimlik).first()
        if patient1:
            return jsonify({'status': 'success', 'message': 'Başarılı'})
        elif len(tckimlik) < 10:
            return jsonify({'status': 'error', 'message': 'Tc kimlik numarası eksik girildi'})
        else:
            return jsonify({'status': 'error', 'message': 'Tc kimlik numarası hatalı'})
        
    return render_template("patient-login.html")

@auth.route('/doctor-login',methods = ['GET','POST'])
def doctor_login():
    if request.method == 'POST':
        tckimlik = request.form.get('tc-kimlik-doctor')
        year = request.form.get('year-doctor')
        month = request.form.get('month-doctor')
        day = request.form.get('day-doctor')

        doctor1 = doctor.query.filter_by(doctorID=tckimlik).first()
        if doctor1:
            return jsonify({'status': 'success', 'message': 'Başarılı'})
        elif len(tckimlik) < 10:
            return jsonify({'status': 'error', 'message': 'Tc kimlik numarası eksik girildi'})
        else:
            return jsonify({'status': 'error', 'message': 'Tc kimlik numarası hatalı'})
        
    return render_template("doctor-login.html")
