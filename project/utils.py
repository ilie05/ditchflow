import random
import re


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


def send_notification(id):
    pass


def mock_sensors(sensors):
    for sensor in sensors:
        sensor['status'] = random.choice([True, False])
        sensor['battery'] = 12.5
        sensor['temp'] = 84.7
        sensor['water'] = 23
        sensor['float'] = random.choice([True, False])

    return sensors


def mock_notification_sensor():
    mocks = [{'address': 'address0', 'name': 'name0'}, {'address': 'address1', 'name': 'name1'},
             {'address': 'address2', 'name': 'name2'}, {'address': 'address3', 'name': 'name3'},
             {'address': 'address4', 'name': 'name4'}, {'address': 'address5', 'name': 'name5'}]

    idx = random.randrange(len(mocks))

    battery = random.randrange(90, 130)
    temperature = random.randrange(800, 1200)
    water = random.randrange(10, 50)
    float = random.choice([True, False])
    float = 'UP' if float else 'DOWN'
    name = mocks[idx]['name']
    address = mocks[idx]['address']

    return address, f'{name},{float},{battery},{battery},{temperature},{water}'


def check_email(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return re.search(regex, email)
