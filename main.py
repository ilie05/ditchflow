import jwt
from flask import Blueprint, render_template, request, url_for, redirect, flash, current_app, Response
from flask_login import login_required, current_user
import traceback
import datetime
from database import db
from models import Sensor, Message, Valve, LabelMessage, Land, Check, Set, Config, LandConfig
from utils import validate_message, validate_labels, write_settings

main = Blueprint('main', __name__)


@main.route('/', )
@login_required
def index():
    cache = current_app.config.get("CACHE")['buttons']
    start_time = current_app.config['CACHE']['start_time']
    token = jwt.encode({'email': current_user.email}, current_app.config.get("JWT_SECRET"),
                       algorithm='HS256').decode()
    run_time = None
    if start_time:
        run_time = datetime.datetime.now().replace(microsecond=0) - start_time

    config_page = Config.query.filter_by(active=True).first()
    config_name = config_page.name if config_page else None
    sets = Set.query.all()
    is_autorun = cache['is_autorun'] if 'is_autorun' in cache else None
    is_paused = cache['is_paused'] if 'is_paused' in cache else None
    return render_template('index.html', jwt_token=str(token), sets=sets, config_name=config_name, run_time=run_time,
                           is_autorun=is_autorun, is_paused=is_paused)


@main.route('/sensors', methods=["GET", "POST", "DELETE"])
@login_required
def sensor():
    if request.method == 'GET':
        sensors = Sensor.query.all()
        token = jwt.encode({'email': current_user.email}, current_app.config.get("JWT_SECRET"),
                           algorithm='HS256').decode()
        return render_template('sensors.html', sensors=sensors, jwt_token=str(token))
    elif request.method == 'POST':
        # update land number
        payload = request.get_json()
        sensor_id = payload['sensorId'] if 'sensorId' in payload else None
        land_number = payload['landNumber'] if 'landNumber' in payload else None

        land = create_land(land_number)
        sensor = Sensor.query.filter_by(id=sensor_id).first()
        sensor.land_id = land.id
        db.session.commit()
        return Response(status=200)
    else:
        payload = request.get_json()
        sensor_id = payload['sensorId'] if 'sensorId' in payload else None

        try:
            sensor = Sensor.query.filter_by(id=sensor_id).first()
            db.session.delete(sensor)
            db.session.commit()
        except Exception as e:
            traceback.print_exc()
            return Response(status=404)
        return Response(status=200)


@main.route('/valves', methods=['GET', 'POST', 'DELETE'])
@login_required
def valve():
    if request.method == 'GET':
        valves = Valve.query.all()
        token = jwt.encode({'email': current_user.email}, current_app.config.get("JWT_SECRET"),
                           algorithm='HS256').decode()
        return render_template('valves.html', valves=valves, jwt_token=str(token))
    elif request.method == 'POST':
        # update land number
        payload = request.get_json()
        valve_id = payload['valveId'] if 'valveId' in payload else None
        land_number = payload['landNumber'] if 'landNumber' in payload else None

        land = create_land(land_number)
        valve = Valve.query.filter_by(id=valve_id).first()
        valve.land_id = land.id
        db.session.commit()
        return Response(status=200)
    else:
        payload = request.get_json()
        valve_id = payload['valveId'] if 'valveId' in payload else None

        try:
            valve = Valve.query.filter_by(id=valve_id).first()
            db.session.delete(valve)
            db.session.commit()
        except Exception as e:
            traceback.print_exc()
            return Response(status=404)
        return Response(status=200)


@main.route('/checks', methods=['GET', 'POST', 'DELETE'])
@login_required
def check():
    if request.method == 'GET':
        checks = Check.query.all()
        sets = Set.query.all()
        token = jwt.encode({'email': current_user.email}, current_app.config.get("JWT_SECRET"),
                           algorithm='HS256').decode()
        return render_template('checks.html', checks=checks, sets=sets, jwt_token=str(token))
    elif request.method == 'POST':
        # update land number
        payload = request.get_json()
        check_id = payload['checkId'] if 'checkId' in payload else None
        set_id = payload['setId'] if 'setId' in payload else None

        check = Check.query.filter_by(id=check_id).first()
        check.set_id = set_id
        db.session.commit()
        return Response(status=200)
    else:
        payload = request.get_json()
        check_id = payload['checkId'] if 'checkId' in payload else None

        try:
            check = Check.query.filter_by(id=check_id).first()
            db.session.delete(check)
            db.session.commit()
        except Exception as e:
            traceback.print_exc()
            return Response(status=404)
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
    labels = [label.to_dict() for label in LabelMessage.query.all()]
    msgs = [message.to_dict() for message in Message.query.all()]
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


@main.route('/calibrate', methods=['POST'])
@login_required
def calibrate():
    return Response(status=200)


def create_land(land_number):
    land = Land.query.filter_by(number=land_number).first()
    if not land:
        land = Land(number=land_number)
        db.session.add(land)

        # add land configs for each config page
        config_pages = Config.query.all()
        for config_page in config_pages:
            land_config = LandConfig(land_id=land.id, config_id=config_page.id)
            db.session.add(land_config)
        db.session.commit()

    return land
