import random


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


def mock_sensors(sensors):
    for sensor in sensors:
        sensor['status'] = random.choice([True, False])
        sensor['battery'] = 12.5
        sensor['temp'] = 84.7
        sensor['water'] = 23
        sensor['float'] = random.choice([True, False])

    return sensors
