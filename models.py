from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from database import db


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


class Carrier(db.Model, SerializerMixin):
    __tablename__ = 'carrier'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100))
    children = db.relationship("Contact")


class Contact(db.Model, SerializerMixin):
    __tablename__ = 'contact'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    cell_number = db.Column(db.String(100))
    email = db.Column(db.String(100))
    carrier_id = db.Column(db.Integer, db.ForeignKey('carrier.id'))
    notify = db.Column(db.Boolean, default=True)


class Message(db.Model, SerializerMixin):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    mess_type = db.Column(db.String(20))
    message = db.Column(db.String(1000))


class LabelMessage(db.Model, SerializerMixin):
    __tablename__ = 'label_message'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)


class Sensor(db.Model, SerializerMixin):
    __tablename__ = 'sensor'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    land_id = db.Column(db.Integer, db.ForeignKey('land.id'))
    status = db.Column(db.Boolean, default=True)
    battery = db.Column(db.Float)
    temperature = db.Column(db.Float)
    water = db.Column(db.Float)
    float = db.Column(db.Boolean)
    delay = db.Column(db.Integer, default=5)
    address = db.Column(db.String(100), unique=True)
    last_update = db.Column(db.DateTime)


class Valve(db.Model, SerializerMixin):
    __tablename__ = 'valve'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    land_id = db.Column(db.Integer, db.ForeignKey('land.id'))
    status = db.Column(db.Boolean, default=True)
    actuator_status = db.Column(db.String(100))
    actuator_position = db.Column(db.Integer)
    battery = db.Column(db.Float)
    temperature = db.Column(db.Float)
    water = db.Column(db.Float)
    preflow = db.Column(db.Integer, default=10)
    run = db.Column(db.Integer, default=90)
    address = db.Column(db.String(100), unique=True)
    last_update = db.Column(db.DateTime)


class Land(db.Model, SerializerMixin):
    __tablename__ = 'land'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True)
    set_id = db.Column(db.Integer, db.ForeignKey('set.id'))

    serialize_rules = ('-sensors.land', '-valves.land',)

    sensors = db.relationship("Sensor", backref='land')
    valves = db.relationship("Valve", backref='land')


class Set(db.Model, SerializerMixin):
    __tablename__ = 'set'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True)

    serialize_rules = ('-lands.set',)

    lands = db.relationship("Land", backref='set')
