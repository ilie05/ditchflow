from models import Message
from utils import format_message


def send_email(message):
    # logic for sending the email
    print(f'formatted_message: {message}')


def send_status_notification(sensor, message_type):
    message = Message.query.filter_by(name=message_type).first().message
    formatted_message = format_message(message, sensor)
    send_email(format_message)
