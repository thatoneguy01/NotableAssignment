from google.cloud import datastore
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/datastore"]
SERVICE_ACCOUNT_FILE = 'C:\\Users\\Daniel\\PycharmProjects\\NotableAssignment\\positive-guild-303723-64991f0d6c7e.json'
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
datastore_client = datastore.Client(project="positive-guild-303723", credentials=credentials)

def create_entity(key, properties):
    entity = datastore.Entity(key=datastore_client.key(key))
    entity.update(properties)
    datastore_client.put(entity)
    return entity

def list_entities(key, limit, order=None):
    query = datastore_client.query(kind=key)
    if order:
        query.order = order
    entities = query.fetch(limit=limit)
    return entities


class Doctor:

    def __init__(self, first_name, last_name, create=True):
        self.first_name = first_name
        self.last_name = last_name
        if create:
            self.entity = create_entity("doctor", {"first_name": self.first_name,"last_name":self.last_name})
            self.id = self.entity.id

    @staticmethod
    def list(limit):
        return [Doctor.from_entity(e) for e in list_entities("doctor", limit, ["last_name"])]

    @staticmethod
    def for_id(id):
        doc_entity = datastore_client.get(datastore_client.key("doctor", int(id)))
        if not doc_entity:
            return None
        doc = Doctor(first_name=doc_entity["first_name"], last_name=doc_entity["last_name"], create=False)
        doc.entity = doc_entity
        doc.id = doc_entity.id
        return doc

    @staticmethod
    def from_entity(entity):
        doc = Doctor(first_name=entity["first_name"], last_name=entity["last_name"], create=False)
        doc.entity = entity
        doc.id = entity.id
        return doc

    def get_appointments(self):
        query = datastore_client.query(kind="appointment")
        query.add_filter("doctor_id", '=', self.id)
        # import pdb
        # pdb.set_trace()
        return [Appointment.from_entity(e) for e in query.fetch(limit=100)]

    def to_dict(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "id":self.id
        }


class Appointment:

    def __init__(self, patient_first_name, patient_last_name, doctor_id, datetime, patient_kind, create=True):
        self.patient_first_name = patient_first_name
        self.patient_last_name = patient_last_name
        self.datetime = datetime
        self.patient_kind = patient_kind
        self.doctor_id = doctor_id
        if create:
            self.entity = create_entity("appointment",
                                        {"patient_first_name": self.patient_first_name,
                                         "patient_last_name":self.patient_last_name,
                                         "doctor_id": self.doctor_id,
                                         "datetime": self.datetime,
                                         "patient_kind": self.patient_kind,
                                         }
                                        )
            self.id = self.entity.id

    @staticmethod
    def for_id(id):
        app_entity = datastore_client.get(datastore_client.key("appointment", int(id)))
        if not app_entity:
            return None
        app = Appointment(patient_first_name=app_entity["patient_first_name"],
                          patient_last_name=app_entity["patient_last_name"],
                          datetime=app_entity["datetime"],
                          patient_kind=app_entity["patient_kind"],
                          doctor_id=app_entity["doctor_id"],
                          create=False)
        app.entity = app_entity
        app.id = app_entity.id
        return app

    @staticmethod
    def from_entity(entity):
        app = Appointment(patient_first_name=entity["patient_first_name"],
                          patient_last_name=entity["patient_last_name"],
                          datetime=entity["datetime"],
                          patient_kind=entity["patient_kind"],
                          doctor_id=entity["doctor_id"],
                          create=False)
        app.entity = entity
        app.id = entity.id
        return app

    def delete(self):
        datastore_client.delete(datastore_client.key("appointment", int(self.id)))

    def to_dict(self):
        return {
            "patient_first_name": self.patient_first_name,
            "patient_last_name": self.patient_last_name,
            "datetime": self.datetime,
            "patient_kind": self.patient_kind,
            "doctor_id": self.doctor_id,
            "id": self.id
        }

