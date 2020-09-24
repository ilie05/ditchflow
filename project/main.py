import jwt
from flask import Blueprint, render_template, request, url_for, redirect, flash, current_app, jsonify, Response
from flask_login import login_required, current_user
from sqlalchemy import exc
from database import db
import datetime
from models import Sensor, Message, Valve, LabelMessage
from utils import validate_message, validate_labels, mock_sensors, write_settings

main = Blueprint('main', __name__)


@main.route('/', )
@login_required
def index():
    return render_template('index.html')


@main.route('/sensors', methods=["GET", "POST", "DELETE"])
@login_required
def sensor():
    if request.method == 'GET':
        sensors = [sensor.as_dict() for sensor in Sensor.query.all()]
        token = jwt.encode({'email': current_user.email}, current_app.config.get("JWT_SECRET"),
                           algorithm='HS256').decode()
        return render_template('sensors.html', sensors=sensors, jwt_token=str(token))
    elif request.method == 'POST':
        # update land number
        payload = request.get_json()
        sensor_id = payload['sensorId'] if 'sensorId' in payload else None
        land_number = payload['landNumber'] if 'landNumber' in payload else None

        sensor = Sensor.query.filter_by(id=sensor_id).first()
        sensor.land_number = land_number
        try:
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return Response(status=409)

        return Response(status=200)
    else:
        payload = request.get_json()
        sensor_id = payload['sensorId'] if 'sensorId' in payload else None

        Sensor.query.filter_by(id=sensor_id).delete()
        db.session.commit()

        return Response(status=200)


@main.route('/valves', methods=['GET', 'POST', 'DELETE'])
@login_required
def valve():
    if request.method == 'GET':
        valves = [valve.as_dict() for valve in Valve.query.all()]
        token = jwt.encode({'email': current_user.email}, current_app.config.get("JWT_SECRET"),
                           algorithm='HS256').decode()
        return render_template('valves.html', valves=valves, jwt_token=str(token))
    elif request.method == 'POST':
        # update land number
        payload = request.get_json()
        valve_id = payload['valveId'] if 'valveId' in payload else None
        land_number = payload['landNumber'] if 'landNumber' in payload else None

        valve = Valve.query.filter_by(id=valve_id).first()
        valve.land_number = land_number
        try:
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return Response(status=409)

        return Response(status=200)
    else:
        payload = request.get_json()
        valve_id = payload['valveId'] if 'valveId' in payload else None

        Valve.query.filter_by(id=valve_id).delete()
        db.session.commit()

        return Response(status=200)


@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'GET':
        return render_template('settings.html', field_name=current_app.config.get("FIELD_NAME"))
    else:
        field_name = request.form.get('fieldName')
        current_app.config['FIELD_NAME'] = field_name
        write_settings({'FIELD_NAME': field_name})
        return redirect(url_for('main.settings'))


@main.route('/messages', methods=["GET", "POST"])
@login_required
def messages():
    labels = [label.as_dict() for label in LabelMessage.query.all()]
    msgs = [message.as_dict() for message in Message.query.all()]
    if request.method == 'GET':
        return render_template('messages.html', labels=labels, messages=msgs)
    else:
        fields = request.form.to_dict()
        for field in fields:
            # form field name format: 'status_valve' or 'battery_sensor'
            message = fields[field]
            mess_name = field.split('_')[0]
            mess_type = field.split('_')[1]
            mess_labels = validate_message(message)
            if not mess_labels and mess_labels != []:
                flash(f'Incorrect message format for {mess_name.upper()} {mess_type.upper()}')
            else:
                if not validate_labels(labels, mess_labels):
                    flash(f'Invalid labels for {mess_name.upper()} {mess_type.upper()} message')
                    continue
                db_message = Message.query.filter_by(name=mess_name, mess_type=mess_type).first()
                db_message.message = message
                db.session.commit()
        return redirect(url_for('main.messages'))
