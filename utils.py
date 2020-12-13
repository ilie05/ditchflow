from flask import current_app
from digi.xbee.devices import XBeeDevice
import random
import re
import urllib.request
import json
import os
import time
from models import Land, Check
from database import db


def validate_message(message):
    """
    :param message: input message string
    :return:  - None if the string format is incorrect
              - if the string is Valid, then return a list with found labels
    """

    labels = []
    label = ''
    bracket_found = False
    for c in message:
        if c == '{':
            if bracket_found:
                return None
            else:
                bracket_found = True
        elif c == '}':
            if bracket_found:
                labels.append(label)
                label = ''
                bracket_found = False
            else:
                return None
        elif bracket_found:
            label += c

    if bracket_found:
        return None

    return labels


def validate_labels(labels, mess_labels):
    """
    :param mess_type: message for 'sensor' or 'valve'
    :param mess_labels: list of labels from message
    :param labels: list of available labels from database
    :return: True if all labels are valid, False either way
    """

    labels = [label['name'] for label in labels]

    for mess_label in mess_labels:
        if mess_label not in labels:
            return False

    return True


def format_message(message, dev_obj):
    is_check = False
    if isinstance(dev_obj, Check):
        is_check = True

    dev_obj = dev_obj.to_dict()

    # add field_name label to the dev-object
    dev_obj['field_name'] = current_app.config.get("FIELD_NAME")

    if is_check:
        dev_obj['land_number'] = '---'
    else:
        dev_obj['land_number'] = dev_obj['land']['number']

    # get labels from the message
    labels = validate_message(message)
    if labels is None:
        return

    for label in labels:
        message = message.replace('{' + label + '}', str(dev_obj[label]))

    return message


def format_phone_number(number):
    res = ''
    digits = [str(n) for n in list(range(10))]
    for c in number:
        if c in digits:
            res += c
    return res


def remove_tags(text):
    TAG_RE = re.compile(r'<[^>]+>')
    text = TAG_RE.sub('', text)
    return text.strip()


def mock_device_data():
    sensors_mocks = [{'address': 'address0', 'name': 'sensor0'}, {'address': 'address1', 'name': 'sensor1'},
                     {'address': 'address2', 'name': 'sensor2'}, {'address': 'address3', 'name': 'sensor3'},
                     {'address': 'address4', 'name': 'sensor4'}, {'address': 'address5', 'name': 'sensor5'}]

    valves_mocks = [{'address': 'address0', 'name': 'valve0'}, {'address': 'address1', 'name': 'valve1'},
                    {'address': 'address2', 'name': 'valve2'}, {'address': 'address3', 'name': 'valve3'},
                    {'address': 'address4', 'name': 'valve4'}, {'address': 'address5', 'name': 'valve5'}]

    checks_mocks = [{'address': 'address0', 'name': 'check0'}, {'address': 'address1', 'name': 'check1'},
                    {'address': 'address2', 'name': 'check2'}, {'address': 'address3', 'name': 'check3'},
                    {'address': 'address4', 'name': 'check4'}, {'address': 'address5', 'name': 'check5'}]

    stats = ['Idle', 'Moving', 'Error']
    mess_type = random.choice(['s', 'v', 'c'])

    if mess_type == 's':
        # generate sensor data
        idx = random.randrange(len(sensors_mocks))

        battery = random.randrange(90, 130)
        temperature = random.randrange(800, 1200)
        water = random.randrange(0, 1200)
        float = random.choice([True, False])
        float = 'UP' if float else 'DOWN'
        name = sensors_mocks[idx]['name']
        address = sensors_mocks[idx]['address']

        return address, f'S,{name},{float},{battery},{temperature},{water}'
    elif mess_type == 'v':
        # generate valve data
        idx = random.randrange(len(valves_mocks))

        name = valves_mocks[idx]['name']
        actuator_status_idx = random.randrange(len(stats))
        actuator_status = stats[actuator_status_idx]
        actuator_position = random.randrange(0, 100)
        battery = random.randrange(90, 130)
        temperature = random.randrange(800, 1200)
        water = random.randrange(0, 1200)
        address = valves_mocks[idx]['address']

        return address, f'V,{name},{actuator_status},{actuator_position},{battery},{temperature},{water}'
    elif mess_type == 'c':
        # generate check data
        idx = random.randrange(len(checks_mocks))

        name = checks_mocks[idx]['name']
        actuator_status_idx = random.randrange(len(stats))
        actuator_status = stats[actuator_status_idx]
        actuator_position = random.randrange(0, 100)
        battery = random.randrange(90, 130)
        temperature = random.randrange(800, 1200)
        water = random.randrange(0, 1200)
        address = checks_mocks[idx]['address']

        return address, f'C,{name},{actuator_status},{actuator_position},{battery},{temperature},{water}'


def check_email(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return re.search(regex, email)


def load_config_settings(app):
    current_folder = os.path.dirname(os.path.abspath(__file__))
    settings_file = os.path.join(current_folder, 'settings.json')
    with open(settings_file) as config_file:
        config_data = json.load(config_file)
        app.config.update(config_data)


def write_settings(data):
    current_folder = os.path.dirname(os.path.abspath(__file__))
    settings_file = os.path.join(current_folder, 'settings.json')
    with open(settings_file) as config_file:
        config_data = json.load(config_file)
        with open(settings_file, 'w') as f:
            for key in data:
                config_data[key] = data[key]
            json.dump(config_data, f)


def mock_battery_temp():
    battery = random.randrange(90, 130)
    temperature = random.randrange(800, 1200)

    return f'{battery},{temperature}'


def reset_xbee():
    try:
        import RPi.GPIO as GPIO
    except Exception as e:
        print(str(e))
        print("COULD NOT IMPORT RPi.GPIO package")

    rst_xbee = 40
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(rst_xbee, GPIO.OUT)
    GPIO.output(rst_xbee, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(rst_xbee, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.cleanup()


def prepopulate_db():
    land = Land.query.filter_by(number=1).first()
    if not land:
        land = Land(number=1)
        db.session.add(land)
        db.session.commit()


def ping_outside():
    interval = current_app.config.get("PING_INTERVAL") * 60
    while True:
        time.sleep(interval)
        urllib.request.urlopen('http://google.com/')
        print("Ping Google....")


def connect_to_device():
    try:
        port = current_app.config.get("DEVICE_PORT")
        baud_rate = current_app.config.get("BAUD_RATE")
        device = XBeeDevice(port, baud_rate)

        device.open()
        device.flush_queues()
        current_app.config['CACHE']['device'] = device
    except Exception as e:
        print("!!!...CONNECTION TO THE DEVICE FAILED...!!!")
        print(str(e))


class RemoteDevice:
    def __init__(self, local_device, address):
        self.address = address


class Device:
    def send_data(self, remote_device, message):
        print(f"Message {message} sent to the device with address: {remote_device.address}")

# 1. Hit start: all the valves in set1 will open to the RUN
# 2. If all the sensors in a specific land trip, then trigger the preflow for all the valves in the next set(all lands),
# then close the valves from that land that triggered the preflow
# 3. When all the sensors will trip in the first set(from all lands),
# then open all the valves to the RUN the next set(all lands),
# then close all the valves in the previous set

# check if the xbee api retrieved a response, if the message is not delivered,
# try again one more time, or display an error

# before closing the valves on first set: send the preflow for each valve in the second set, wait for MOVING status,
# then wait for IDLE status, then check if the Preflow == current position (+-1% error),
# then close the valves on set one
# do the same for the RUN


# STOP will close all the valves, reset the clock
# PAUSE time goes on, does not do anything
