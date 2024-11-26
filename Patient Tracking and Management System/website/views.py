from flask import Blueprint, render_template, jsonify, request, current_app, send_file
from datetime import datetime
from . import db
from .models import appointment, doctor, patient, FileUpload
import os
from werkzeug.utils import secure_filename


views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("base.html")

# Randevu durumunu kontrol eden API rotası
@views.route('/get-appointment-status')
def get_appointment_status_api():
    doctor_id = request.args.get('doctor_id')
    date = request.args.get('date')
    hour = request.args.get('hour')

    year, month, day = map(int, date.split('-'))

    hour = int(hour.split(':')[0])

    date_obj = datetime(year, month, day)
    status = get_appointment_status(doctor_id, date_obj, hour)

    return jsonify({'status': status})

# Doktor takvimi sayfasını gösteren rota
@views.route('/doctor-schedule/<doctor_id>')
def doctor_schedule(doctor_id):
    return render_template('doctor_schedule.html', doctor_id=doctor_id)

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
    else:
        return 'Açık'

@views.route('/get_doctors_by_department', methods=['POST'])
def get_doctors_by_department():
    department = request.json.get('department')

    doctors = doctor.query.filter_by(specialty=department).all()
    doctor_list = [{"id": doctor.doctorID, "name": f"Dr. {doctor.name} {doctor.surname}"} for doctor in doctors]
    return jsonify(doctor_list)

@views.route('/book_appointment', methods=['POST'])
def book_appointment():
    data = request.get_json()
    doctor_id = data.get('doctorID')
    patient_id = data.get('patientID')
    appointment_time = data.get('time')
    day = data.get('day')

    existing_appointment = appointment.query.filter_by(
        doctorID=doctor_id,
        day=day,
        hour=appointment_time
    ).first()

    if existing_appointment:
        return jsonify({'status': 'error', 'message': 'Bu saat için zaten bir randevu alınmış.'})

    new_appointment = appointment(
        doctorID=doctor_id,
        patientID=patient_id,
        year=datetime.now().year,
        month=datetime.now().month,
        day=day,
        hour=appointment_time
    )
    db.session.add(new_appointment)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Randevu başarıyla alındı!'})

@views.route('/patient-login', methods=['POST'])
def patient_login():
    tckimlik = request.form.get('tc-kimlik')
    year = request.form.get('year')
    month = request.form.get('month')
    day = request.form.get('day')

    patient1 = patient.query.filter_by(patientID=tckimlik).first()

    if patient1:
        patient_id = patient1.patientID
        return jsonify({
            'status': 'success',
            'message': 'Başarılı giriş yapıldı.',
            'patient_id': patient_id
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Geçersiz TC Kimlik No.'
        })
    
@views.route('/doctor-login', methods=['POST'])
def doctor_login():
    tc_kimlik = request.form.get('tc-kimlik-doctor')
    year = request.form.get('year-doctor')
    month = request.form.get('month-doctor')
    day = request.form.get('day-doctor')

    doctor1 = doctor.query.filter_by(doctorID=tc_kimlik).first()

    if doctor1:
        doctor_id = doctor1.doctorID
        return jsonify({
            'status': 'success',
            'message': 'Giriş başarılı',
            'doctorID': doctor1.doctorID,
            'doctor_name': f'{doctor1.name} {doctor1.surname}'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Giriş başarısız. Bilgilerinizi kontrol edin.'
        })

@views.route('/get_appointments', methods=['GET'])
def get_appointments():
    patient_id = request.args.get('patientID') 
    appointments = appointment.query.filter_by(patientID=patient_id).all()
    
    appointments_data = []
    for app in appointments:
        doctor1 = doctor.query.get(app.doctorID)
        appointment_info = {
            'date': f"{app.day}-{app.month}-{app.year}",
            'time': f"{app.hour}",
            'department': doctor1.specialty,
            'doctor_name': f"{doctor1.name} {doctor1.surname}"
        }
        appointments_data.append(appointment_info)

    return jsonify({'appointments': appointments_data})

@views.route('/get_doctor_appointments', methods=['GET'])
def get_doctor_appointments():
    doctor_id = request.args.get('doctorID')
    appointments = appointment.query.filter_by(doctorID=doctor_id).all()
    doctor1 = doctor.query.filter_by(doctorID=doctor_id).first()

    appointments_data = []
    for app in appointments:
        patient1 = patient.query.get(app.patientID)
        appointment_info = {
            'date': f"{app.day}-{app.month}-{app.year}",
            'time': f"{app.hour}",
            'department': f"{doctor1.specialty}",
            'patient_name': f"{patient1.name} {patient1.surname}",
            'randevuID': f"{app.randevuID}"
        }
        appointments_data.append(appointment_info)

    return jsonify({'appointments': appointments_data})

@views.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'randevuID' not in request.form:
        return jsonify({'status': 'error', 'message': 'Dosya veya randevu ID eksik.'})

    file = request.files['file']
    randevuID = request.form['randevuID']

    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'Dosya seçilmedi.'})

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        new_file = FileUpload(
            randevuID=randevuID,
            file_path=file_path,
            upload_date=datetime.utcnow()
        )
        db.session.add(new_file)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Dosya başarıyla yüklendi.'})
    return jsonify({'status': 'error', 'message': 'Dosya yüklenemedi.'})

@views.route('/get_doctor_reports', methods=['GET'])
def get_doctor_reports():
    doctorID = request.args.get('doctorID')
    
    reports = FileUpload.query.join(appointment, FileUpload.randevuID == appointment.randevuID) \
    .join(patient, appointment.patientID == patient.patientID) \
    .filter(appointment.doctorID == doctorID).all()
    
    report_list = []
    for report in reports:
        patient1 = patient.query.get(report.appointment.patientID)
        report_info = {
            'appointment_date': f"{report.appointment.year}-{report.appointment.month}-{report.appointment.day}",
            'patient_name': f"{patient1.name} {patient1.surname}",
            'fileID': report.fileID
        }
        report_list.append(report_info)

    return jsonify({'reports': report_list})

@views.route('/download_report', methods=['GET'])
def download_report():
    fileID = request.args.get('fileID')
    report = FileUpload.query.filter_by(fileID=fileID).first()

    if report:
        # Get the absolute file path using os.path.abspath
        file_path = os.path.abspath(report.file_path)
        
        # Check if the file exists before sending
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'status': 'error', 'message': 'Dosya bulunamadı.'})
    else:
        return jsonify({'status': 'error', 'message': 'Rapor bulunamadı.'})

@views.route('/get_patient_results', methods=['GET'])
def get_patient_results():
    patientID = request.args.get('patientID')
    
    results = FileUpload.query.join(appointment, FileUpload.randevuID == appointment.randevuID) \
        .join(doctor, appointment.doctorID == doctor.doctorID) \
        .filter(appointment.patientID == patientID).all()
    
    result_list = []
    for result in results:
        doctor_info = doctor.query.get(result.appointment.doctorID)
        result_info = {
            'appointment_date': f"{result.appointment.year}-{result.appointment.month}-{result.appointment.day}",
            'department': f"{doctor_info.specialty}",
            'doctor_name': f"{doctor_info.name} {doctor_info.surname}",
            'fileID': result.fileID
        }
        result_list.append(result_info)

    return jsonify({'results': result_list})


