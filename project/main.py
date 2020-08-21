# main.py
import jwt
from flask import Blueprint, render_template, request, url_for, redirect, flash, current_app, jsonify
from flask_login import login_required, current_user
import datetime
from database import db
from models import Sensor, Message
from utils import validate_message, validate_labels, mock_sensors

main = Blueprint('main', __name__)


@main.route('/moreSensors', methods=["POST"])
@login_required
def more_sensors():
    payload = request.get_json()
    page = payload['page'] if 'page' in payload else None
    if page is None:
        return jsonify([])

    try:
        page = int(page)
        if page < 0:
            raise ValueError
        sensors = [sensor.as_dict() for sensor in Sensor.query.offset(6 + page * 3).limit(3)]
        sensors = mock_sensors(sensors)
        return jsonify(sensors)
    except ValueError:
        return jsonify([])


@main.route('/')
@login_required
def index():
    sensors = [sensor.as_dict() for sensor in Sensor.query.limit(6)]
    sensors = mock_sensors(sensors)
    token = jwt.encode({'email': current_user.email}, current_app.config.get("JWT_SECRET"), algorithm='HS256').decode()
    return render_template('index.html', sensors=sensors, jwt_token=str(token))


@main.route('/messages', methods=["GET", "POST"])
@login_required
def messages():
    msgs = [msg.as_dict() for msg in Message.query.all()]
    exclude_fields = ['sensorName', 'landNumber', 'fieldName']
    filtered_msgs = filter(lambda label: label['name'] not in exclude_fields, msgs)
    if request.method == 'GET':
        return render_template('messages.html', labels=filtered_msgs)
    else:
        for message in filtered_msgs:
            field = request.form.get(message['name'])
            print(field)
            labels = validate_message(field)
            if not labels and labels != []:
                flash(f'Incorrect message format for {message["name"].upper()}')
            else:
                if not validate_labels(labels, msgs):
                    flash(f'Invalid labels for {message["name"].upper()}')
                    continue
                db_message = Message.query.filter_by(name=message["name"]).first()
                db_message.message = field
                db.session.commit()
        return redirect(url_for('main.messages'))


@main.route('/populate')
def populate():
    for i in range(10):
        sensor = Sensor(name=f'Sensor {i + 1}', last_update=datetime.datetime.now().replace(microsecond=0))
        db.session.add(sensor)
    db.session.commit()
    return 'Populate Sensor table'


@main.route('/populatelabel')
def populatelabel():
    sensor = Message(name='status', message='')
    db.session.add(sensor)
    sensor = Message(name='battery', message='')
    db.session.add(sensor)
    sensor = Message(name='temperature', message='')
    db.session.add(sensor)
    sensor = Message(name='float', message='')
    db.session.add(sensor)
    sensor = Message(name='water', message='')
    db.session.add(sensor)
    sensor = Message(name='sensorName', message='')
    db.session.add(sensor)
    sensor = Message(name='landNumber', message='')
    db.session.add(sensor)
    sensor = Message(name='fieldName', message='')
    db.session.add(sensor)

    db.session.commit()
    return 'Populate Label table'
