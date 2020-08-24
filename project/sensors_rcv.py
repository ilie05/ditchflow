from flaskthreads import AppContextThread
from digi.xbee.devices import XBeeDevice, XBee64BitAddress
from models import Message, Sensor
from database import db
import datetime
from flask_login import current_user
import time

# local_xbee = XBeeDevice("COM1", 9600)
# remote_xbee = RemoteXBeeDevice(local_xbee, XBee64BitAddress.from_hex_string("0013A20012345678"))


def create_update_sensor(message, address):
    sensor = Sensor.query.filter_by(address=address).first()

    if not sensor:
        # does not exist, create one
        sensor = Sensor(name=message[0], address=address, last_update=datetime.datetime.now().replace(microsecond=0))
        db.session.add(sensor)
    else:
        # exists, update the name and the date
        sensor.name = message[0]
        sensor.status = True
        sensor.float = True if message[1] == 'UP' else False
        sensor.battery = int(message[2]) / 10
        sensor.temperature = int(message[3]) / 10
        sensor.water = int(message[4]) / 10
        sensor.last_update = datetime.datetime.now().replace(microsecond=0)
    db.session.commit()


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
        # mess = Message.query.filter_by(name='water').first()
        # mess.message = f'A lot of data here {i}'
        # db.session.add(mess)
        # db.session.commit()
        # print(mess.message)
        print(i)
        print("\n\n")
        socket_io.emit('newnumber', {'number': i}, namespace='/sensor')
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
