from flaskthreads import AppContextThread
from models import Sensor, Valve, Land, Check, Config, SensorConfig, ValveConfig, CheckConfig
import datetime
import traceback
import random
from flask import current_app
from flask_login import current_user
import time
from database import db
from utils import mock_device_data, ping_outside, check_online_status, send_status_notification
from serial_rcv import update_battery_temp_test, update_battery_temp, get_gps_data_test, get_gps_data


def create_update_sensor(message, address, signal_strength):
    try:
        current_time = datetime.datetime.now().replace(microsecond=0)
        name = message[0]
        float = True if message[1] == 'UP' else False
        trip_time = current_time if float else None
        battery = int(message[2]) / 10
        temperature = int(message[3]) / 10

        # delete the sensor if there is data when the same sensor name but different address
        sensor = Sensor.query.filter(Sensor.name == name, Sensor.address != address).first()
        if sensor:
            db.session.delete(sensor)
            db.session.commit()

        sensor = Sensor.query.filter_by(address=address).first()

        if not sensor:
            # does not exist, create one
            land = Land.query.filter_by(number=1).first()
            sensor = Sensor(name=name, battery=battery, float=float, temperature=temperature,
                            signal_strength=signal_strength, land_id=land.id, address=address, last_update=current_time,
                            trip_time=trip_time)
            db.session.add(sensor)
            db.session.commit()

            # add sensor configs for each config page
            config_pages = Config.query.all()
            for config_page in config_pages:
                sensor_config = SensorConfig(sensor_id=sensor.id, config_id=config_page.id)
                db.session.add(sensor_config)
        else:
            # exists, update the name and the date
            sensor.name = name
            sensor.status = True
            sensor.float = float
            sensor.trip_time = trip_time
            sensor.battery = battery
            sensor.temperature = temperature
            sensor.signal_strength = signal_strength
            sensor.last_update = current_time
        db.session.commit()

        return {'id': sensor.id, 'name': name, 'last_update': str(current_time), 'battery': battery,
                'float': float, 'temperature': temperature, 'signal_strength': signal_strength}, sensor
    except Exception as e:
        print(e)
        print("INVALID DATA FROM SENSORS")


def create_update_valve(message, address):
    valve = Valve.query.filter_by(address=address).first()
    current_time = datetime.datetime.now().replace(microsecond=0)

    try:
        name = message[0]
        actuator_status = message[1]
        actuator_position = int(message[2])
        battery = int(message[3]) / 10
        temperature = int(message[4]) / 10
        water = int(message[5]) / 10

        if water < 0 or water > 99.9:
            water = None

        if not valve:
            # does not exist, create one
            land = Land.query.filter_by(number=1).first()
            valve = Valve(name=name, battery=battery, actuator_status=actuator_status,
                          actuator_position=actuator_position, temperature=temperature, water=water, land_id=land.id,
                          address=address, last_update=current_time)
            db.session.add(valve)
            db.session.commit()

            # add sensor configs for each config page
            config_pages = Config.query.all()
            for config_page in config_pages:
                valve_config = ValveConfig(valve_id=valve.id, config_id=config_page.id)
                db.session.add(valve_config)
        else:
            # exists, update the name and the date
            valve.name = name
            valve.status = True
            valve.actuator_status = actuator_status
            valve.actuator_position = actuator_position
            valve.battery = battery
            valve.temperature = temperature
            valve.water = water
            valve.last_update = current_time
        db.session.commit()
        return {'id': valve.id, 'name': name, 'last_update': str(current_time), 'battery': battery,
                'actuator_status': actuator_status, 'actuator_position': actuator_position,
                'temperature': temperature, 'water': water}, valve
    except Exception as e:
        print(e)
        print("INVALID DATA FROM VALVES")


def create_update_check(message, address):
    check = Check.query.filter_by(address=address).first()
    current_time = datetime.datetime.now().replace(microsecond=0)

    try:
        name = message[0]
        actuator_status = message[1]
        actuator_position = int(message[2])
        battery = int(message[3]) / 10
        temperature = int(message[4]) / 10
        water = int(message[5]) / 10

        if water < 0 or water > 99.9:
            water = None

        if not check:
            # does not exist, create one
            check = Check(name=name, battery=battery, actuator_status=actuator_status,
                          actuator_position=actuator_position, temperature=temperature, water=water, address=address,
                          last_update=current_time)
            db.session.add(check)
            db.session.commit()

            # add check configs for each config page
            config_pages = Config.query.all()
            for config_page in config_pages:
                check_config = CheckConfig(check_id=check.id, config_id=config_page.id)
                db.session.add(check_config)
        else:
            # exists, update the name and the date
            check.name = name
            check.status = True
            check.actuator_status = actuator_status
            check.actuator_position = actuator_position
            check.battery = battery
            check.temperature = temperature
            check.water = water
            check.last_update = current_time
        db.session.commit()
        return {'id': check.id, 'name': name, 'last_update': str(current_time), 'battery': battery,
                'actuator_status': actuator_status, 'actuator_position': actuator_position,
                'temperature': temperature, 'water': water}, check
    except Exception as e:
        print(e)
        print("INVALID DATA FROM VALVES")


def receive_sensor_data(socket_io):
    notified_sensor_battery_ids = []
    notified_sensor_float_ids = []
    notified_valve_battery_ids = []
    notified_valve_water_ids = []
    notified_check_battery_ids = []
    notified_check_water_ids = []

    device = current_app.config.get("CACHE")['device']
    print("Waiting for data...\n")

    while True:
        xbee_message = device.read_data()
        if xbee_message is not None:
            # DATA FORMAT:  S,Sensor 1,UP,125,901
            # DATA FORMAT:  V,VALVE 1,IDLE,50,121,700,241
            # DATA FORMAT:  M,121,700
            message = xbee_message.data.decode()
            message = message.split(',')
            mess_type = message[0]
            message = message[1:]

            dev_address = str(xbee_message.remote_device.get_64bit_addr())

            print(f"From {dev_address} >> {message}")

            if mess_type == 'S':
                signal_strength = 255 - int(device.get_parameter("DB").hex(), 16)
                data_to_send, sensor = create_update_sensor(message, dev_address, signal_strength)

                battery = data_to_send['battery']
                float = data_to_send['float']
                if battery < current_app.config.get("BATTERY_MIN_VOLTAGE"):
                    if sensor.id not in notified_sensor_battery_ids:
                        send_status_notification(sensor, 'battery')
                        notified_sensor_battery_ids.append(sensor.id)
                else:
                    if sensor.id in notified_sensor_battery_ids \
                            and battery + 1 > current_app.config.get("BATTERY_MIN_VOLTAGE"):
                        notified_sensor_battery_ids.remove(sensor.id)

                if float:
                    if sensor.id not in notified_sensor_float_ids:
                        send_status_notification(sensor, 'float')
                        notified_sensor_float_ids.append(sensor.id)
                else:
                    if sensor.id in notified_sensor_float_ids:
                        notified_sensor_float_ids.remove(sensor.id)

                socket_io.emit('sensor_notification', data_to_send, namespace='/notification')
                print("\n")
            elif mess_type == 'V':
                data_to_send, valve = create_update_valve(message, dev_address)

                battery = data_to_send['battery']
                water = data_to_send['water']
                if battery < current_app.config.get("BATTERY_MIN_VOLTAGE"):
                    if valve.id not in notified_valve_battery_ids:
                        send_status_notification(valve, 'battery')
                        notified_valve_battery_ids.append(valve.id)
                else:
                    if valve.id in notified_valve_battery_ids \
                            and battery + 1 > current_app.config.get("BATTERY_MIN_VOLTAGE"):
                        notified_valve_battery_ids.remove(valve.id)

                if water is not None and water > current_app.config.get("WATER_MAX_LEVEL"):
                    if valve.id not in notified_valve_water_ids:
                        send_status_notification(valve, 'water')
                        notified_valve_water_ids.append(valve.id)
                else:
                    if valve.id in notified_valve_water_ids:
                        notified_valve_water_ids.remove(valve.id)

                socket_io.emit('valve_notification', data_to_send, namespace='/notification')
            elif mess_type == 'C':
                data_to_send, check = create_update_check(message, dev_address)

                battery = data_to_send['battery']
                water = data_to_send['water']
                if battery < current_app.config.get("BATTERY_MIN_VOLTAGE"):
                    if check.id not in notified_check_battery_ids:
                        send_status_notification(check, 'battery')
                        notified_check_battery_ids.append(check.id)
                else:
                    if check.id in notified_check_battery_ids \
                            and battery + 1 > current_app.config.get("BATTERY_MIN_VOLTAGE"):
                        notified_check_battery_ids.remove(check.id)

                if water is not None and water > current_app.config.get("WATER_MAX_LEVEL"):
                    if check.id not in notified_check_water_ids:
                        send_status_notification(check, 'water')
                        notified_check_water_ids.append(check.id)
                else:
                    if check.id in notified_check_water_ids:
                        notified_check_water_ids.remove(check.id)

                socket_io.emit('check_notification', data_to_send, namespace='/notification')
            else:
                raise Exception("Invalid data type from XBee Module")


def receive_sensor_data_test(socket_io):
    notified_sensor_battery_ids = []
    notified_sensor_float_ids = []
    notified_valve_battery_ids = []
    notified_valve_water_ids = []
    notified_check_battery_ids = []
    notified_check_water_ids = []

    while True:
        time.sleep(3)
        dev_address, message = mock_device_data()
        print("Generated data...")
        print(dev_address, message)
        message = message.split(',')
        mess_type = message[0]
        message = message[1:]

        if mess_type == 'S':
            signal_strength = 255 - random.randrange(80)
            data_to_send, sensor = create_update_sensor(message, dev_address, signal_strength)

            battery = data_to_send['battery']
            float = data_to_send['float']
            if battery < current_app.config.get("BATTERY_MIN_VOLTAGE"):
                if sensor.id not in notified_sensor_battery_ids:
                    send_status_notification(sensor, 'battery')
                    notified_sensor_battery_ids.append(sensor.id)
            else:
                if sensor.id in notified_sensor_battery_ids \
                        and battery + 1 > current_app.config.get("BATTERY_MIN_VOLTAGE"):
                    notified_sensor_battery_ids.remove(sensor.id)

            if float:
                if sensor.id not in notified_sensor_float_ids:
                    send_status_notification(sensor, 'float')
                    notified_sensor_float_ids.append(sensor.id)
            else:
                if sensor.id in notified_sensor_float_ids:
                    notified_sensor_float_ids.remove(sensor.id)

            socket_io.emit('sensor_notification', data_to_send, namespace='/notification')
            print("\n")
        elif mess_type == 'V':
            data_to_send, valve = create_update_valve(message, dev_address)

            battery = data_to_send['battery']
            water = data_to_send['water']
            if battery < current_app.config.get("BATTERY_MIN_VOLTAGE"):
                if valve.id not in notified_valve_battery_ids:
                    send_status_notification(valve, 'battery')
                    notified_valve_battery_ids.append(valve.id)
            else:
                if valve.id in notified_valve_battery_ids \
                        and battery + 1 > current_app.config.get("BATTERY_MIN_VOLTAGE"):
                    notified_valve_battery_ids.remove(valve.id)

            if water is not None and water > current_app.config.get("WATER_MAX_LEVEL"):
                if valve.id not in notified_valve_water_ids:
                    send_status_notification(valve, 'water')
                    notified_valve_water_ids.append(valve.id)
            else:
                if valve.id in notified_valve_water_ids:
                    notified_valve_water_ids.remove(valve.id)

            socket_io.emit('valve_notification', data_to_send, namespace='/notification')
        elif mess_type == 'C':
            data_to_send, check = create_update_check(message, dev_address)

            battery = data_to_send['battery']
            water = data_to_send['water']
            if battery < current_app.config.get("BATTERY_MIN_VOLTAGE"):
                if check.id not in notified_check_battery_ids:
                    send_status_notification(check, 'battery')
                    notified_check_battery_ids.append(check.id)
            else:
                if check.id in notified_check_battery_ids \
                        and battery + 1 > current_app.config.get("BATTERY_MIN_VOLTAGE"):
                    notified_check_battery_ids.remove(check.id)

            if water is not None and water > current_app.config.get("WATER_MAX_LEVEL"):
                if check.id not in notified_check_water_ids:
                    send_status_notification(check, 'water')
                    notified_check_water_ids.append(check.id)
            else:
                if check.id in notified_check_water_ids:
                    notified_check_water_ids.remove(check.id)

            socket_io.emit('check_notification', data_to_send, namespace='/notification')
        else:
            raise Exception("Invalid data type from XBee Module")


def listen_sensors_thread(socket_io):
    t1 = AppContextThread(target=thread_wrap(receive_sensor_data), args=(socket_io,))
    print("***Listen sensors thread before running***")
    t1.start()

    t2 = AppContextThread(target=thread_wrap(check_online_status), args=(socket_io,))
    print("***Check Status Sensor-Valve-Check thread before running***")
    t2.start()

    t3 = AppContextThread(target=thread_wrap(update_battery_temp), args=(socket_io,))
    print("***Battery-Temperature thread before running***")
    t3.start()

    t4 = AppContextThread(target=thread_wrap(ping_outside))
    print("***PING thread before running***")
    t4.start()

    t5 = AppContextThread(target=thread_wrap(get_gps_data))
    print("***GPS thread before running***")
    t5.start()

    @socket_io.on('connect', namespace='/notification')
    def test_connect():
        if not current_user.is_authenticated:
            print("NOT AUTHENTICATED!")
            return False
        print("CONNECTED")


def thread_wrap(thread_func):
    def wrapper(*args, **kwargs):
        while True:
            try:
                thread_func(*args, **kwargs)
            except BaseException as e:
                traceback.print_exc()
                print(f'{str(e)}; restarting thread')
            else:
                traceback.print_exc()
                print('Exited normally, bad thread; restarting')
            time.sleep(2)

    return wrapper
