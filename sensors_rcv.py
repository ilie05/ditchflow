from flaskthreads import AppContextThread
from digi.xbee.devices import XBeeDevice
from models import Sensor, Valve, Land, Check, Config, SensorConfig, ValveConfig, CheckConfig
import datetime
import traceback
import serial
from flask import current_app
from flask_login import current_user
import time
import threading
from database import db
from utils import mock_device_data, mock_battery_temp, reset_xbee
from email_service import send_status_notification, send_email

lock = threading.Lock()


# local_xbee = XBeeDevice("COM1", 9600)
# remote_xbee = RemoteXBeeDevice(local_xbee, XBee64BitAddress.from_hex_string("0013A20012345678"))


def create_update_sensor(message, address):
    sensor = Sensor.query.filter_by(address=address).first()
    current_time = datetime.datetime.now().replace(microsecond=0)
    try:
        name = message[0]
        float = True if message[1] == 'UP' else False
        battery = int(message[2]) / 10
        temperature = int(message[3]) / 10
        water = int(message[4]) / 10

        if water < 0 or water > 99.9:
            water = None

        if not sensor:
            # does not exist, create one
            land = Land.query.filter_by(number=1).first()
            sensor = Sensor(name=name, battery=battery, float=float, temperature=temperature, water=water,
                            land_id=land.id, address=address, last_update=current_time)
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
            sensor.battery = battery
            sensor.temperature = temperature
            sensor.water = water
            sensor.last_update = current_time
        db.session.commit()

        return {'id': sensor.id, 'name': name, 'last_update': str(current_time), 'battery': battery,
                'float': float, 'temperature': temperature, 'water': water}, sensor
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
    notified_sensor_water_ids = []
    notified_valve_battery_ids = []
    notified_valve_water_ids = []
    notified_check_battery_ids = []
    notified_check_water_ids = []

    port = current_app.config.get("DEVICE_PORT")
    baud_rate = current_app.config.get("BAUD_RATE")
    device = XBeeDevice(port, baud_rate)
    try:
        device.open()
        device.flush_queues()
        print("Waiting for data...\n")

        while True:
            xbee_message = device.read_data()
            if xbee_message is not None:
                # DATA FORMAT:  S,Sensor 1,UP,125,901,241
                # DATA FORMAT:  V,VALVE 1,IDLE,50,121,700,241
                # DATA FORMAT:  M,121,700
                message = xbee_message.data.decode()
                message = message.split(',')
                mess_type = message[0]
                message = message[1:]

                dev_address = str(xbee_message.remote_device.get_64bit_addr())

                print(f"From {dev_address} >> {message}")

                if mess_type == 'S':
                    data_to_send, sensor = create_update_sensor(message, dev_address)

                    battery = data_to_send['battery']
                    water = data_to_send['water']
                    float = data_to_send['float']
                    if battery < current_app.config.get("BATTERY_MIN_VOLTAGE"):
                        if sensor.id not in notified_sensor_battery_ids:
                            send_status_notification(sensor, 'battery')
                            notified_sensor_battery_ids.append(sensor.id)
                    else:
                        if sensor.id in notified_sensor_battery_ids:
                            notified_sensor_battery_ids.remove(sensor.id)

                    if float:
                        if sensor.id not in notified_sensor_float_ids:
                            send_status_notification(sensor, 'float')
                            notified_sensor_float_ids.append(sensor.id)
                    else:
                        if sensor.id in notified_sensor_float_ids:
                            notified_sensor_float_ids.remove(sensor.id)

                    if water is not None and water > current_app.config.get("WATER_MAX_LEVEL"):
                        if sensor.id not in notified_sensor_water_ids:
                            send_status_notification(sensor, 'water')
                            notified_sensor_water_ids.append(sensor.id)
                    else:
                        if sensor.id in notified_sensor_water_ids:
                            notified_sensor_water_ids.remove(sensor.id)

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
                        if valve.id in notified_valve_battery_ids:
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
                        if check.id in notified_check_battery_ids:
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
    finally:
        if device is not None and device.is_open():
            device.close()


def receive_sensor_data_test(socket_io):
    notified_sensor_battery_ids = []
    notified_sensor_float_ids = []
    notified_sensor_water_ids = []
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
            data_to_send, sensor = create_update_sensor(message, dev_address)

            battery = data_to_send['battery']
            float = data_to_send['float']
            water = data_to_send['water']
            if battery < current_app.config.get("BATTERY_MIN_VOLTAGE"):
                if sensor.id not in notified_sensor_battery_ids:
                    send_status_notification(sensor, 'battery')
                    notified_sensor_battery_ids.append(sensor.id)
            else:
                if sensor.id in notified_sensor_battery_ids:
                    notified_sensor_battery_ids.remove(sensor.id)

            if float:
                if sensor.id not in notified_sensor_float_ids:
                    send_status_notification(sensor, 'float')
                    notified_sensor_float_ids.append(sensor.id)
            else:
                if sensor.id in notified_sensor_float_ids:
                    notified_sensor_float_ids.remove(sensor.id)

            if water is not None and water > current_app.config.get("WATER_MAX_LEVEL"):
                if sensor.id not in notified_sensor_water_ids:
                    send_status_notification(sensor, 'water')
                    notified_sensor_water_ids.append(sensor.id)
            else:
                if sensor.id in notified_sensor_water_ids:
                    notified_sensor_water_ids.remove(sensor.id)

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
                if valve.id in notified_valve_battery_ids:
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
                if check.id in notified_check_battery_ids:
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


def check_online_status(socket_io):
    notified_sensor_ids = []
    notified_valve_ids = []
    notified_check_ids = []
    while True:
        time.sleep(current_app.config.get("CHECK_FOR_STATUS_TIME"))  # every 10 sec.
        db.session.commit()
        sensors = Sensor.query.all()
        valves = Valve.query.all()
        checks = Check.query.all()
        check_status_device(socket_io, sensors, notified_sensor_ids)
        check_status_device(socket_io, valves, notified_valve_ids)
        check_status_device(socket_io, checks, notified_check_ids)


def check_status_device(socket_io, devices, notified_ids):
    check_time = current_app.config.get("GO_OFFLINE_SENSOR_TIME")  # 30 min.
    current_time = datetime.datetime.now().replace(microsecond=0)
    for device in devices:
        last_update = device.last_update
        total_diff = current_time - last_update
        total_diff_sec = total_diff.total_seconds()
        if total_diff_sec > check_time:
            device.status = False
            db.session.add(device)
            db.session.commit()
            if device.id not in notified_ids:
                send_status_notification(device, 'status')
                notified_ids.append(device.id)
            if isinstance(device, Sensor):
                socket_io.emit('goOfflineSensor', device.id, namespace='/notification')
            elif isinstance(device, Valve):
                socket_io.emit('goOfflineValve', device.id, namespace='/notification')
            elif isinstance(device, Check):
                socket_io.emit('goOfflineCheck', device.id, namespace='/notification')

        else:
            if device.id in notified_ids:
                notified_ids.remove(device.id)


def update_battery_temp(socket_io):
    notified = False
    min_battery_val = current_app.config.get("SYSTEM_BATTERY_MIN_VOLTAGE")
    while True:
        with serial.Serial(current_app.config.get("MAIN_SYSTEM_DEVICE_PORT"), 9600, timeout=3) as ser:
            data = ser.read(7)
            data = data.decode()
            if data:
                message = data.split(',')

                battery = int(message[0]) / 10
                temperature = int(message[1]) / 10

                if battery < min_battery_val:
                    if not notified:
                        send_email(current_app.config.get("SYSTEM_BATTERY_MESSAGE"))
                        notified = True
                else:
                    notified = False

                socket_io.emit('batteryTemp', {'battery': battery, 'temperature': temperature},
                               namespace='/notification')


def update_battery_temp_test(socket_io):
    notified = False
    min_battery_val = current_app.config.get("SYSTEM_BATTERY_MIN_VOLTAGE")
    while True:
        time.sleep(5)
        message = mock_battery_temp()
        message = message.split(',')

        battery = int(message[0]) / 10
        temperature = int(message[1]) / 10

        if battery < min_battery_val:
            if not notified:
                send_email(current_app.config.get("SYSTEM_BATTERY_MESSAGE"))
                notified = True
        else:
            notified = False

        socket_io.emit('batteryTemp', {'battery': battery, 'temperature': temperature}, namespace='/notification')


def listen_sensors_thread(socket_io):
    try:
        reset_xbee()
    except Exception as e:
        print(str(e))
        print("COULD NOT RESET THE XBEE!")

    t1 = AppContextThread(target=thread_wrap(receive_sensor_data), args=(socket_io,))
    print("***Listen sensors thread before running***")
    t1.start()

    t2 = AppContextThread(target=thread_wrap(check_online_status), args=(socket_io,))
    print("***Check Status Sensor-Valve-Check thread before running***")
    t2.start()

    t3 = AppContextThread(target=thread_wrap(update_battery_temp), args=(socket_io,))
    print("***Battery-Temperature thread before running***")
    t3.start()

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

    return wrapper
