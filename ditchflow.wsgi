import sys

activate_this = '/var/www/ditchflow/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

sys.path.insert(0, '/var/www/ditchflow')

from app import socket_io, app as application
from sensors_rcv import listen_sensors_thread

context = application.app_context()
context.push()

with context:
    listen_sensors_thread(socket_io)
