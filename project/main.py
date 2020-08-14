# main.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
import datetime
from database import db
from models import Sensor

main = Blueprint('main', __name__)


@main.route('/')
def index():
    sensors = [sensor.as_dict() for sensor in Sensor.query.all()]
    sensor = Sensor(name='Sensor 1', land_number="45",  last_update=datetime.datetime.now())
    # db.session.add(sensor)
    # db.session.commit()
    return render_template('index.html')






