from flask import session, g, Blueprint, Response, current_app
from flask_login import current_user, login_required
from digi.xbee.devices import RemoteXBeeDevice, XBee64BitAddress
import time
import datetime

autorun = Blueprint('autorun', __name__)


@autorun.route('/startAutorun')
@login_required
def start_autorun():
    cache = current_app.config.get("CACHE")['buttons']
    cache['is_autorun'] = True
    current_app.config['CACHE']['buttons'] = cache
    current_app.config['CACHE']['start_time'] = datetime.datetime.now().replace(microsecond=0)
    return Response(status=200)


@autorun.route('/stopAutorun')
@login_required
def stop_autorun():
    cache = current_app.config.get("CACHE")['buttons']
    cache['is_autorun'] = False
    cache['is_paused'] = None
    current_app.config['CACHE']['buttons'] = cache
    current_app.config['CACHE']['start_time'] = None
    return Response(status=200)


@autorun.route('/pauseAutorun')
@login_required
def pause_autorun():
    cache = current_app.config.get("CACHE")['buttons']
    is_paused = cache['is_paused'] if 'is_paused' in cache else None
    is_autorun = cache['is_autorun'] if 'is_autorun' in cache else None
    if not is_autorun:
        return Response(status=200)

    if is_paused:
        # unpause
        cache['is_paused'] = False
    else:
        # pause
        cache['is_paused'] = True

    current_app.config['CACHE']['buttons'] = cache
    return Response(status=200)


try:
    local_device = g.local_device
    remote_device = RemoteXBeeDevice(local_device, XBee64BitAddress.from_hex_string("0013A20041C2A987"))

    # Send data using the remote object.
    while True:
        time.sleep(5)
        local_device.send_data(remote_device, "Hello XBee!")
except Exception as e:
    print("Sending error caught....")
    print(str(e))
