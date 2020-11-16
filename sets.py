import jwt
from flask import Blueprint, render_template, request, url_for, redirect, current_app, Response
from flask_login import login_required, current_user
from database import db
from models import Land, Set, Valve, Sensor, Check

sets = Blueprint('sets', __name__)


@sets.route('/configuration', methods=["GET", "POST", "DELETE"])
@login_required
def configuration():
    if request.method == 'GET':
        token = jwt.encode({'email': current_user.email}, current_app.config.get("JWT_SECRET"),
                           algorithm='HS256').decode()
        lands = Land.query.filter_by(set_id=None).order_by(Land.number).all()
        lands = list(filter(lambda l: len(l.sensors) > 0 or len(l.valves) > 0, lands))
        sets = Set.query.all()
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


@sets.route('/startpreflow', methods=["POST"])
@login_required
def startpreflow():
    payload = request.get_json()
    t = payload['t'] if 't' in payload else None
    obj_id = payload['objId'] if 'objId' in payload else None
    field_val = payload['fieldVal'] if 'fieldVal' in payload else None

    if t == 'v':
        obj = Valve.query.filter_by(id=obj_id).first()
        if str(obj.preflow) != field_val:
            obj.preflow = field_val
            db.session.add(obj)
            db.session.commit()
            return Response(status=200)
    elif t == 'c':
        obj = Check.query.filter_by(id=obj_id).first()
        if str(obj.start) != field_val:
            obj.start = field_val
            db.session.add(obj)
            db.session.commit()
            return Response(status=200)
    else:
        return Response(status=404)

    return Response(status=201)


@sets.route('/run', methods=["POST"])
@login_required
def run():
    payload = request.get_json()
    t = payload['t'] if 't' in payload else None
    obj_id = payload['objId'] if 'objId' in payload else None
    run = payload['run'] if 'run' in payload else None

    if t == 'v':
        obj = Valve.query.filter_by(id=obj_id).first()
    elif t == 'c':
        obj = Check.query.filter_by(id=obj_id).first()
    else:
        return Response(status=404)
    if str(obj.run) != run:
        obj.run = run
        db.session.add(obj)
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
    t = payload['t'] if 't' in payload else None
    obj_id = payload['objId'] if 'objId' in payload else None
    is_checked = payload['isChecked'] if 'isChecked' in payload else None

    if t == 'v':
        obj = Land.query.filter_by(id=obj_id).first()
    elif t == 'c':
        obj = Set.query.filter_by(id=obj_id).first()
    else:
        return Response(status=404)

    obj.autorun = is_checked
    db.session.add(obj)
    db.session.commit()

    return Response(status=200)


@sets.route('/beforeafter', methods=["POST"])
@login_required
def beforeafter():
    payload = request.get_json()
    obj_id = payload['objId'] if 'objId' in payload else None
    is_checked = payload['isChecked'] if 'isChecked' in payload else None

    check = Check.query.filter_by(id=obj_id).first()
    check.before_after = is_checked
    db.session.add(check)
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
