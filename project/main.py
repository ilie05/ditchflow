import jwt
from flask import Blueprint, render_template, request, url_for, redirect, flash, current_app, jsonify, Response
from flask_login import login_required, current_user
from sqlalchemy import exc
from database import db
from models import Sensor, Message
from utils import validate_message, validate_labels, mock_sensors

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


@main.route('/messages', methods=["GET", "POST"])
@login_required
def messages():
    msgs = [msg.as_dict() for msg in Message.query.all()]
    exclude_fields = ['name', 'land_number', 'field_name', 'water', 'temperature']
    filtered_msgs = filter(lambda label: label['name'] not in exclude_fields, msgs)
    if request.method == 'GET':
        return render_template('messages.html', labels=filtered_msgs, lbs=msgs)
    else:
        for message in filtered_msgs:
            field = request.form.get(message['name'])
            labels = validate_message(field)
            if not labels and labels != []:
                flash(f'Incorrect message format for {message["name"].upper()}')
            else:
                if not validate_labels(labels, msgs):
                    flash(f'Invalid labels for {message["name"].upper()} message')
                    continue
                db_message = Message.query.filter_by(name=message["name"]).first()
                db_message.message = field
                db.session.commit()
        return redirect(url_for('main.messages'))
