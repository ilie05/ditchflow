from flask import current_app
import random
import re
import json


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


def validate_labels(labels, messages):
    """
    :param labels: list of labels from message
    :param messages: list of messages
    :return: True if all labels are valid, False either way
    """

    valid_labels = [message['name'] for message in messages]

    for label in labels:
        if label not in valid_labels:
            return False

    return True


def format_message(message, sensor):
    sensor = sensor.as_dict()
    sensor['field_name'] = current_app.config.get("FIELD_NAME")
    labels = validate_message(message)
    if labels is None:
        return

    for label in labels:
        replace_str = str(sensor[label])
        if label == 'status':
            replace_str = 'ONLINE' if sensor[label] else 'OFFLINE'
        elif label == 'float':
            replace_str = 'UP' if sensor[label] else 'DOWN'
        message = message.replace('{' + label + '}', replace_str)

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


def mock_sensors(sensors):
    for sensor in sensors:
        sensor['status'] = random.choice([True, False])
        sensor['battery'] = 12.5
        sensor['temp'] = 84.7
        sensor['water'] = 23
        sensor['float'] = random.choice([True, False])

    return sensors


def mock_device_data():
    sensors_mocks = [{'address': 'address0', 'name': 'sensor0'}, {'address': 'address1', 'name': 'sensor1'},
                     {'address': 'address2', 'name': 'sensor2'}, {'address': 'address3', 'name': 'sensor3'},
                     {'address': 'address4', 'name': 'sensor4'}, {'address': 'address5', 'name': 'sensor5'}]

    valves_mocks = [{'address': 'address0', 'name': 'valve0'}, {'address': 'address1', 'name': 'valve1'},
                    {'address': 'address2', 'name': 'valve2'}, {'address': 'address3', 'name': 'valve3'},
                    {'address': 'address4', 'name': 'valve4'}, {'address': 'address5', 'name': 'valve5'}]

    mess_type = random.choice([True, False])

    if mess_type:
        # generate sensor data
        idx = random.randrange(len(sensors_mocks))

        battery = random.randrange(90, 130)
        temperature = random.randrange(800, 1200)
        water = random.randrange(10, 50)
        float = random.choice([True, False])
        float = 'UP' if float else 'DOWN'
        name = sensors_mocks[idx]['name']
        address = sensors_mocks[idx]['address']

        return address, f'S,{name},{float},{battery},{temperature},{water}'
    else:
        stats = ['Idle', 'Moving', 'Error']
        # generate valve data
        idx = random.randrange(len(valves_mocks))

        name = valves_mocks[idx]['name']
        actuator_status_idx = random.randrange(len(stats))
        actuator_status = stats[actuator_status_idx]
        actuator_position = random.randrange(0, 100)
        battery = random.randrange(90, 130)
        temperature = random.randrange(800, 1200)
        water = random.randrange(10, 50)
        address = valves_mocks[idx]['address']

        return address, f'V,{name},{actuator_status},{actuator_position},{battery},{temperature},{water}'


def check_email(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return re.search(regex, email)


def load_config_settings(app):
    with open('settings.json') as config_file:
        config_data = json.load(config_file)
        app.config.update(config_data)


def write_settings(data):
    with open('settings.json') as config_file:
        config_data = json.load(config_file)
        with open('settings.json', 'w') as f:
            for key in data:
                config_data[key] = data[key]
            json.dump(config_data, f)
