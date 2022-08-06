from flask import Flask, request, make_response, jsonify
from data import Doctor, Appointment
from datetime import datetime, timezone

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'hello test'


@app.route("/create_doctor")
def create_doctor():
    name = request.args.get("name")
    first_name, last_name = name.split(' ')
    doc = Doctor(first_name=first_name, last_name=last_name)
    return make_response(jsonify(doc.to_dict()))


@app.route("/create_appointment")
def create_appointment():
    name = request.args.get("name")
    app_datetime = datetime.fromisoformat(request.args.get("datetime"))
    patient_kind = request.args.get("patient_kind")
    doctor_id = request.args.get("doctor_id")
    first_name, last_name = name.split(' ')
    app = Appointment(patient_first_name=first_name,
                      patient_last_name=last_name,
                      datetime=app_datetime,
                      patient_kind=patient_kind,
                      doctor_id=doctor_id)
    return make_response(app.to_dict())


@app.route("/doctors", methods=["GET"])
def get_doctors():
    limit = request.args.get("limit", 100)
    doctors = [doc.to_dict() for doc in Doctor.list(limit)]
    return make_response(jsonify(doctors))


@app.route("/doctors/<doctor_id>/appointments/<date>", methods=["GET"])
def get_appointments(doctor_id, date):
    app_date = datetime.fromisoformat(date).date()
    doc = Doctor.for_id(doctor_id)
    appointments = doc.get_appointments()
    on_day = [app.to_dict() for app in appointments if app.datetime.date() == app_date]
    return make_response(jsonify(on_day))


@app.route("/appointments/<appointment_id>", methods=["DELETE"])
def delete_appointment(appointment_id):
    appointment = Appointment.for_id(appointment_id)
    appointment.delete()
    return make_response("success", 200)


@app.route("/appointments", methods=["POST"])
def add_appointment():
    request_data = request.json
    name = request_data.get("name")
    app_datetime = datetime.fromisoformat(request_data.get("datetime"))
    app_datetime = app_datetime.replace(tzinfo=timezone.utc)
    patient_kind = request_data.get("patient_kind")
    doctor_id = request_data.get("doctor_id")
    if any([var is None for var in [name, app_datetime, patient_kind, doctor_id]]):
        return make_response("Missing Required field", 400)
    if app_datetime.minute not in [0, 15, 30, 45] and app_datetime.second == 0:
        return make_response("Appointment must start at 15 minute intervals", 400)
    if patient_kind not in ["New Patient", "Follow-up"]:
        return make_response('Patient_kind must be either "New Patient" or "Follow-up"', 400)
    first_name, last_name = name.split(' ')
    doc = Doctor.for_id(doctor_id)
    if not doc:
        return make_response("No doctor with that id", 400)
    appointments_for_doc = doc.get_appointments()
    conflicts = [appointment for appointment in appointments_for_doc if appointment.datetime == app_datetime]
    if len(conflicts) >= 3:
        return make_response("Too many appointments at specified time", 400)
    app = Appointment(patient_first_name=first_name,
                      patient_last_name=last_name,
                      datetime=app_datetime,
                      patient_kind=patient_kind,
                      doctor_id=doctor_id)
    return make_response(jsonify(app.to_dict()))


if __name__ == '__main__':
    app.run()
