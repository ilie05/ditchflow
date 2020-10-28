import jwt
from flask import Blueprint, render_template, request, url_for, redirect, current_app, Response
from flask_login import login_required, current_user
from database import db
from models import Land, Set, Valve, Sensor

sets = Blueprint('sets', __name__)


@sets.route('/configuration', methods=["GET", "POST", "DELETE"])
@login_required
def configuration():
    if request.method == 'GET':
        token = jwt.encode({'email': current_user.email}, current_app.config.get("JWT_SECRET"),
                           algorithm='HS256').decode()
        lands = Land.query.filter_by(set_id=None).order_by(Land.number).all()
        sets = [s.to_dict() for s in Set.query.all()]
        return render_template('sets.html', lands=lands, sets=sets, jwt_token=str(token))
    elif request.method == 'POST':
        try:
            set_number = int(request.form.get('set_number'))
            land_id = int(request.form.get('land_id'))
        except ValueError as e:
            print("Wrong set_number or land_id")
            return redirect(url_for('sets.configuration'))

        set_obj = Set.query.filter_by(number=set_number).first()
        if not set_obj:
            set_obj = Set(number=set_number)
            db.session.add(set_obj)
            db.session.commit()

        land = Land.query.filter_by(id=land_id).first()
        land.set_id = set_obj.id
        db.session.add(land)
        db.session.commit()
        return redirect(url_for('sets.configuration'))
    else:
        payload = request.get_json()
        set_id = payload['setId'] if 'setId' in payload else None
        land_id = payload['landId'] if 'landId' in payload else None

        land = Land.query.filter_by(id=land_id).first()
        land.set_id = None
        db.session.add(land)

        lands = Land.query.filter_by(set_id=set_id).all()
        if len(lands) < 1:
            Set.query.filter_by(id=set_id).delete()

        db.session.commit()
        return Response(status=200)


@sets.route('/preflow', methods=["POST"])
@login_required
def preflow():
    payload = request.get_json()
    valve_id = payload['valveId'] if 'valveId' in payload else None
    preflow = payload['preflow'] if 'preflow' in payload else None

    valve = Valve.query.filter_by(id=valve_id).first()
    if str(valve.preflow) != preflow:
        valve.preflow = preflow
        db.session.add(valve)
        db.session.commit()
        return Response(status=200)

    return Response(status=201)


@sets.route('/valveRun', methods=["POST"])
@login_required
def valveRun():
    payload = request.get_json()
    valve_id = payload['valveId'] if 'valveId' in payload else None
    valve_run = payload['valveRun'] if 'valveRun' in payload else None

    valve = Valve.query.filter_by(id=valve_id).first()
    if str(valve.run) != valve_run:
        valve.run = valve_run
        db.session.add(valve)
        db.session.commit()
        return Response(status=200)

    return Response(status=201)


@sets.route('/delay', methods=["POST"])
@login_required
def delay():
    payload = request.get_json()
    sensor_id = payload['sensorId'] if 'sensorId' in payload else None
    sensor_delay = payload['delay'] if 'delay' in payload else None

    sensor = Sensor.query.filter_by(id=sensor_id).first()
    if str(sensor.delay) != sensor_delay:
        sensor.delay = sensor_delay
        db.session.add(sensor)
        db.session.commit()
        return Response(status=200)

    return Response(status=201)


@sets.route('/autorun', methods=["POST"])
@login_required
def autorun():
    payload = request.get_json()
    land_id = payload['landId'] if 'landId' in payload else None
    is_checked = payload['isChecked'] if 'isChecked' in payload else None

    land = Land.query.filter_by(id=land_id).first()
    land.autorun = is_checked
    db.session.add(land)
    db.session.commit()

    return Response(status=200)


@sets.route('/landdelay', methods=["POST"])
@login_required
def landdelay():
    payload = request.get_json()
    land_id = payload['landId'] if 'landId' in payload else None
    land_delay = payload['delay'] if 'delay' in payload else None

    land = Land.query.filter_by(id=land_id).first()
    land.delay = land_delay
    db.session.add(land)
    db.session.commit()

    return Response(status=200)
