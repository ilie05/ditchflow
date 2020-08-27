import smtplib
import ssl

smtp_server = "smtp.gmail.com"
port = 587
sender = "iliepetrasco@gmail.com"
password = ""
# receiver = "3305185630@vtext.com"
receiver = "petras.moil@gmail.com"

message = f"""Subject: The subject\n\n
data\nsdf
Sensor 1 battery is low."""

with smtplib.SMTP(smtp_server, port=port) as smtp:
    smtp.starttls()
    # context = ssl.create_default_context()
    # smtp.starttls(context=context)
    smtp.login(sender, password)
    smtp.sendmail(sender, receiver, message)
