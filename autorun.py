from digi.xbee.devices import RemoteXBeeDevice, XBee64BitAddress
from flask import Blueprint, Response, current_app
from flask_login import login_required
import psutil
import time
import datetime
from models import Set
from utils import Device, RemoteDevice
from multiprocessing import Process

autorun = Blueprint('autorun', __name__)


@autorun.route('/startAutorun')
@login_required
def start_autorun():
    cache = current_app.config.get("CACHE")['buttons']
    socket_io = current_app.config.get("SOCKET_IO")
    cache['is_autorun'] = True

    mp = Process(target=start_autorun_callback, args=(socket_io,))
    mp.start()
    current_app.config['CACHE']['autorun_process'] = mp
    p = psutil.Process(mp.pid)
    current_app.config['CACHE']['autorun_process_wrap'] = p

    current_app.config['CACHE']['buttons'] = cache
    current_app.config['CACHE']['start_time'] = datetime.datetime.now().replace(microsecond=0)
    return Response(status=200)


def start_autorun_callback(socket_io):
    sets = Set.query.order_by(Set.number).all()
    for land in sets[0].lands:
        for valve in land.valves:
            valve_config = next(filter(lambda x: x.config.active is True, valve.valve_configs), None)
            try:
                send_valve_position(valve, valve_config.run)
            except Exception:
                try:
                    send_valve_position(valve, valve_config.run)
                except Exception:
                    socket_io.emit('error_push', {'id': valve.id,
                                                  'message': f'Failed to open twice the valve: {valve.name} to the RUN position: {valve_config.run}%!'},
                                   namespace='/notification')

    # try:
    #     local_device = g.local_device
    #     remote_device = RemoteXBeeDevice(local_device, XBee64BitAddress.from_hex_string("0013A20041C2A987"))
    #
    #     # Send data using the remote object.
    #     while True:
    #         time.sleep(5)
    #         local_device.send_data(remote_device, "Hello XBee!")
    # except Exception as e:
    #     print("Sending error caught....")
    #     print(str(e))
    while True:
        time.sleep(1)
        print("INSIDE THREAD")


def send_valve_position(valve, position):
    # local_device = current_app.config.get("CACHE")['device']
    local_device = Device()
    # remote_device = RemoteXBeeDevice(local_device, XBee64BitAddress.from_hex_string(valve.address))
    remote_device = RemoteDevice(local_device, valve.address)
    local_device.send_data(remote_device, position)


@autorun.route('/stopAutorun')
@login_required
def stop_autorun():
    cache = current_app.config.get("CACHE")['buttons']
    cache['is_autorun'] = False
    cache['is_paused'] = None

    autorun_process = current_app.config['CACHE']['autorun_process']
    autorun_process_wrap = current_app.config['CACHE']['autorun_process_wrap']
    if autorun_process.is_alive():
        autorun_process_wrap.resume()
        autorun_process.terminate()
        autorun_process.join()

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

    autorun_process_wrap = current_app.config['CACHE']['autorun_process_wrap']
    autorun_process = current_app.config['CACHE']['autorun_process']
    if is_paused:
        # unpause
        if autorun_process.is_alive():
            autorun_process_wrap.resume()
        cache['is_paused'] = False
    else:
        # pause
        if autorun_process.is_alive():
            autorun_process_wrap.suspend()
        cache['is_paused'] = True

    current_app.config['CACHE']['buttons'] = cache
    return Response(status=200)
