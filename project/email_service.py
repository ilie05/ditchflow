from flask import current_app
import smtplib
from socket import gaierror
from models import Message, Contact, Carrier
from utils import format_message


def send_email(msg):
    port = current_app.config.get("MAIL_PORT")
    smtp_server = current_app.config.get("MAIL_SERVER")
    sender = username = current_app.config.get("MAIL_USERNAME")
    password = current_app.config.get("MAIL_PASSWORD")

    contacts = Contact.query.filter_by(notify=True).all()
    for contact in contacts:
        carrier = Carrier.query.filter_by(id=contact.carrier_id).first()
        if not carrier:
            print(f'*** NO CARRIER FOUND FOR CONTACT NAME: {contact.name}')
            continue

        receiver = [f'{contact.cell_number}@{carrier.email}', contact.email]

        message = f"""Subject: Ditchflow Notification\n\n
        {msg}"""

        print(f'Message to send: {message}')
        print(f'Sending to :{receiver}')
        try:
            with smtplib.SMTP(smtp_server, port) as server:
                server.starttls()
                server.login(username, password)
                server.sendmail(sender, receiver, message)
            print('Sent')
        except (gaierror, ConnectionRefusedError):
            print('Failed to connect to the server. Bad connection settings?')
        except smtplib.SMTPServerDisconnected:
            print('Failed to connect to the server. Wrong user/password?')
        except smtplib.SMTPException as e:
            print('SMTP error occurred: ' + str(e))
        except Exception as e:
            print("Another exception")
            print(str(e))


def send_status_notification(sensor, message_type):
    message = Message.query.filter_by(name=message_type).first().message
    formatted_message = format_message(message, sensor)
    send_email(formatted_message)
