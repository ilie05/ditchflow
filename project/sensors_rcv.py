from flaskthreads import AppContextThread
from digi.xbee.devices import XBeeDevice, XBee64BitAddress
from models import Message, Sensor
from database import db
import datetime
from flask_login import current_user
import time
from utils import mock_notification_sensor


# local_xbee = XBeeDevice("COM1", 9600)
# remote_xbee = RemoteXBeeDevice(local_xbee, XBee64BitAddress.from_hex_string("0013A20012345678"))


def create_update_sensor(message, address, socket_io):
    sensor = Sensor.query.filter_by(address=address).first()
    current_time = datetime.datetime.now().replace(microsecond=0)
    print(f'Recieved data from sensor: address: {address}  data: {message}')
    try:
        name = message[0]
        float = True if message[1] == 'UP' else False
        battery = int(message[2]) / 10
        temperature = int(message[3]) / 10
        water = int(message[4]) / 10

        if not sensor:
            # does not exist, create one
            sensor = Sensor(name=name, address=address, last_update=current_time, battery=battery, float=float,
                            temperature=temperature, water=water)
            db.session.add(sensor)
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
        data_to_send = {'id': sensor.id, 'name': name, 'last_update': str(current_time), 'battery': battery,
                        'float': float, 'temperature': temperature, 'water': water}
        socket_io.emit('sensor_notification', data_to_send, namespace='/sensor')
    except Exception as e:
        print(e)
        print("INVALID DATA FROM SENSORS")


def thread_function():
    PORT = "/dev/ttyAMA0"
    BAUD_RATE = 9600
    device = XBeeDevice(PORT, BAUD_RATE)
    try:
        device.open()

        device.flush_queues()

        print("Waiting for data...\n")

        while True:
            xbee_message = device.read_data()
            if xbee_message is not None:
                # DATA FORMAT:  Sensor 1,UP,125,901,241
                rcv_data = xbee_message.data.decode()
                rcv_data = rcv_data.split(',')

                dev_address = xbee_message.remote_device.get_64bit_addr()

                print(f"From {dev_address} >> {rcv_data}")

                create_update_sensor(rcv_data, dev_address)
    finally:
        if device is not None and device.is_open():
            device.close()


def test_callback(socket_io):
    i = 0
    while True:
        time.sleep(3)
        address, message = mock_notification_sensor()
        print(address, message)
        message = message.split(',')
        create_update_sensor(message, address, socket_io)
        # mess = Message.query.filter_by(name='water').first()
        # mess.message = f'A lot of data here {i}'
        # db.session.add(mess)
        # db.session.commit()
        # print(mess.message)
        print(i)
        print("\n\n")

        i += 1


def listen_to_sensors(socket_io):
    t = AppContextThread(target=test_callback, args=(socket_io,))
    print("Sensors receive thread before running")
    t.start()

    @socket_io.on('connect', namespace='/sensor')
    def test_connect():
        if not current_user.is_authenticated:
            print("NOT AUTHENTICATED!")
            return False
        print("CONNECTED")
