from flask import current_app
import smtplib
import telnyx
from socket import gaierror
from models import Contact


def send_sms(msg):
    telnyx.api_key = current_app.config.get("TELNYX_KEY")
    your_telnyx_number = current_app.config.get("TELNYX_NUMBER")

    contacts = Contact.query.filter_by(notify=True).all()
    for contact in contacts:
        destination_number = f'+1{contact.cell_number}'
        telnyx.Message.create(from_=your_telnyx_number, to=destination_number, text=msg, )


def send_email(msg):
    port = current_app.config.get("MAIL_PORT")
    smtp_server = current_app.config.get("MAIL_SERVER")
    sender = username = current_app.config.get("MAIL_USERNAME")
    password = current_app.config.get("MAIL_PASSWORD")

    contacts = Contact.query.filter_by(notify=True).all()
    send_sms(msg)
    for contact in contacts:
        receiver = contact.email
        message = f"""Subject: DitchFlow Notification\n\n {msg}"""

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
