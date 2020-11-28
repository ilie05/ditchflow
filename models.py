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
    address = db.Column(db.String(100), unique=True)
    last_update = db.Column(db.DateTime)

    serialize_rules = ('-sensor_configs.sensor',)
    sensor_configs = db.relationship("SensorConfig", backref='sensor', cascade='all,delete')


class SensorConfig(db.Model, SerializerMixin):
    __tablename__ = 'sensor_config'

    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'))
    config_id = db.Column(db.Integer, db.ForeignKey('config.id'))
    delay = db.Column(db.Integer, default=5)


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
    address = db.Column(db.String(100), unique=True)
    last_update = db.Column(db.DateTime)

    serialize_rules = ('-valve_configs.valve',)
    valve_configs = db.relationship("ValveConfig", backref='valve', cascade='all,delete')


class ValveConfig(db.Model, SerializerMixin):
    __tablename__ = 'valve_config'

    id = db.Column(db.Integer, primary_key=True)
    valve_id = db.Column(db.Integer, db.ForeignKey('valve.id'))
    config_id = db.Column(db.Integer, db.ForeignKey('config.id'))
    preflow = db.Column(db.Integer, default=10)
    run = db.Column(db.Integer, default=90)


class Land(db.Model, SerializerMixin):
    __tablename__ = 'land'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True)
    autorun = db.Column(db.Boolean, default=True)
    delay = db.Column(db.Integer, default=5)
    set_id = db.Column(db.Integer, db.ForeignKey('set.id'))

    serialize_rules = ('-sensors.land', '-valves.land',)
    sensors = db.relationship("Sensor", backref='land')
    valves = db.relationship("Valve", backref='land')


class Set(db.Model, SerializerMixin):
    __tablename__ = 'set'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True)
    autorun = db.Column(db.Boolean, default=True)

    serialize_rules = ('-lands.set', '-checks.set',)
    lands = db.relationship("Land", backref='set')
    checks = db.relationship("Check", backref='set')


class Check(db.Model, SerializerMixin):
    __tablename__ = 'check'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    set_id = db.Column(db.Integer, db.ForeignKey('set.id'))
    status = db.Column(db.Boolean, default=True)
    actuator_status = db.Column(db.String(100))
    actuator_position = db.Column(db.Integer)
    battery = db.Column(db.Float)
    temperature = db.Column(db.Float)
    water = db.Column(db.Float)
    address = db.Column(db.String(100), unique=True)
    last_update = db.Column(db.DateTime)

    serialize_rules = ('-check_configs.check',)
    check_configs = db.relationship("CheckConfig", backref='check', cascade='all,delete')


class CheckConfig(db.Model, SerializerMixin):
    __tablename__ = 'check_config'

    id = db.Column(db.Integer, primary_key=True)
    check_id = db.Column(db.Integer, db.ForeignKey('check.id'))
    config_id = db.Column(db.Integer, db.ForeignKey('config.id'))
    start = db.Column(db.Integer, default=10)
    run = db.Column(db.Integer, default=90)
    before_after = db.Column(db.Boolean, default=True)


class Config(db.Model, SerializerMixin):
    __tablename__ = 'config'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    active = db.Column(db.Boolean, default=True)

    serialize_rules = ('-sensor_configs', '-valve_configs', '-check_configs',)
    sensor_configs = db.relationship("SensorConfig", backref='config', cascade='all,delete')
    valve_configs = db.relationship("ValveConfig", backref='config', cascade='all,delete')
    check_configs = db.relationship("CheckConfig", backref='config', cascade='all,delete')

# open time for valve: set, land, valve , time
# tripping time for sensor: set, land, sensor, time_
