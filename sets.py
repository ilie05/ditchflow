import jwt
from flask import Blueprint, render_template, request, url_for, redirect, current_app, Response, flash
from flask_login import login_required, current_user
from database import db
from models import Land, Set, Valve, Sensor, Check, Config, SensorConfig, ValveConfig, CheckConfig, LandConfig
import traceback

sets = Blueprint('sets', __name__)


@sets.route('/configuration', methods=["GET", "POST", "DELETE"])
@login_required
def configuration():
    if request.method == 'GET':
        config_name = request.args.get("config_name")
        configs = Config.query.all()

        if config_name is None:
            config_page = Config.query.filter_by(active=True).first()
            if config_page:
                return redirect(url_for('sets.configuration', config_name=config_page.name))
            else:
                config_page = Config.query.first()
                if config_page:
                    config_page.active = True
                    db.session.commit()
                    return redirect(url_for('sets.configuration', config_name=config_page.name))
                else:
                    return render_template('sets.html', configs=configs)

        config_page = Config.query.filter_by(name=config_name).first()
        if not config_page:
            return render_template('not_found.html')

        config_pages = Config.query.filter_by(active=True).all()
        for page in config_pages:
            page.active = False
        config_page.active = True
        db.session.commit()

        token = jwt.encode({'email': current_user.email}, current_app.config.get("JWT_SECRET"),
                           algorithm='HS256').decode()
        lands = Land.query.filter_by(set_id=None).order_by(Land.number).all()
        lands = list(filter(lambda l: len(l.sensors) > 0 or len(l.valves) > 0, lands))
        sets = Set.query.order_by(Set.number).all()
        return render_template('sets.html', lands=lands, sets=sets, jwt_token=str(token), configs=configs,
                               config_name=config_name)
    elif request.method == 'POST':
        config_name = request.form.get('config_name')
        if not config_name:
            return redirect(url_for('sets.configuration'))

        config_page = Config.query.filter_by(name=config_name).first()
        if config_page:
            flash('Configuration {} already exists'.format(config_name))
            return redirect(url_for('sets.configuration', config_name=config_name))

        config_pages = Config.query.filter_by(active=True).all()
        for page in config_pages:
            page.active = False

        config_page = Config(name=config_name)
        db.session.add(config_page)
        db.session.commit()

        for sensor in Sensor.query.all():
            sensor_config = SensorConfig(sensor_id=sensor.id, config_id=config_page.id)
            db.session.add(sensor_config)

        for valve in Valve.query.all():
            valve_config = ValveConfig(valve_id=valve.id, config_id=config_page.id)
            db.session.add(valve_config)

        for check in Check.query.all():
            check_config = CheckConfig(check_id=check.id, config_id=config_page.id)
            db.session.add(check_config)

        for land in Land.query.all():
            land_config = LandConfig(land_id=land.id, config_id=config_page.id)
            db.session.add(land_config)

        db.session.commit()
        return redirect(url_for('sets.configuration', config_name=config_name))
    else:
        payload = request.get_json()
        config_name = payload['config_name'] if 'config_name' in payload else None

        try:
            config_page = Config.query.filter_by(name=config_name).first()
            db.session.delete(config_page)
            db.session.commit()
        except Exception as e:
            traceback.print_exc()
            return Response(status=404)
        return Response(status=200)


@sets.route('/config_set', methods=["POST", "DELETE"])
@login_required
def config_set():
    if request.method == 'POST':
        try:
            set_number = int(request.form.get('set_number'))
            land_id = int(request.form.get('land_id'))
        except ValueError as e:
            print("Wrong set_number or land_id")
            traceback.print_exc()
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
        obj = ValveConfig.query.filter_by(id=obj_id).first()
        if str(obj.preflow) != field_val:
            obj.preflow = field_val
            db.session.add(obj)
            db.session.commit()
            return Response(status=200)
    elif t == 'c':
        obj = CheckConfig.query.filter_by(id=obj_id).first()
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
        obj = ValveConfig.query.filter_by(id=obj_id).first()
    elif t == 'c':
        obj = CheckConfig.query.filter_by(id=obj_id).first()
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
    sensor_config_id = payload['sensorConfigId'] if 'sensorConfigId' in payload else None
    sensor_delay = payload['delay'] if 'delay' in payload else None

    sensor = SensorConfig.query.filter_by(id=sensor_config_id).first()
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

    check = CheckConfig.query.filter_by(id=obj_id).first()
    check.before_after = is_checked
    db.session.add(check)
    db.session.commit()

    return Response(status=200)


@sets.route('/landdelay', methods=["POST"])
@login_required
def landdelay():
    payload = request.get_json()
    land_id = payload['landConfigId'] if 'landConfigId' in payload else None
    land_delay = payload['delay'] if 'delay' in payload else None

    land = LandConfig.query.filter_by(id=land_id).first()
    land.delay = land_delay
    db.session.add(land)
    db.session.commit()

    return Response(status=200)


@sets.route('/sendPosition', methods=["POST"])
@login_required
def sendPosition():
    payload = request.get_json()
    t = payload['t'] if 't' in payload else None
    obj_id = payload['objId'] if 'objId' in payload else None
    position = payload['position'] if 'position' in payload else None

    config_page = Config.query.filter_by(active=True).first()
    if t == 'v':
        valve_config = ValveConfig.query.filter_by(valve_id=obj_id, config_id=config_page.id).first()
        if str(valve_config.run) != position:
            valve_config.run = position
            db.session.add(valve_config)
            db.session.commit()
            return Response(status=200)
    elif t == 'c':
        check_config = CheckConfig.query.filter_by(check_id=obj_id, config_id=config_page.id).first()
        if str(check_config.run) != position:
            check_config.run = position
            db.session.add(check_config)
            db.session.commit()
            return Response(status=200)
    else:
        return Response(status=404)

    return Response(status=201)
