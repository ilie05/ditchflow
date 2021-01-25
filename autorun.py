from digi.xbee.devices import RemoteXBeeDevice, XBee64BitAddress
from flask import Blueprint, Response, current_app
from flaskthreads import AppContextThread
from flask_login import login_required
import psutil
from multiprocessing import Process
import time
import datetime
import traceback
from queue import Queue
from database import db
from models import Set, Error, Land, Valve
from utils import Device, RemoteDevice

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
            send_valve_position(valve, valve_config.run, socket_io)

    error_list = validate_move_valves(sets[0].lands, 'run')
    if error_list:
        socket_io.emit('error_push', {'error_list': error_list}, namespace='/notification')
        exit(0)

    set_cnt = 1
    land_flooded = False
    set_flooded = False
    while True:
        time.sleep(60)
        sets = Set.query.order_by(Set.number).all()
        current_set = sets[set_cnt]
        prev_set = sets[set_cnt - 1]

        if not land_flooded:
            for land in prev_set.lands:
                flooded = True
                for sensor in land.sensors:
                    if not sensor.float:
                        flooded = False
                        break
                if flooded:
                    land_flooded = True
                    error_list = preflow_valves(socket_io, current_set, land.sensors, land)
                    if error_list:
                        socket_io.emit('error_push', {'error_list': error_list}, namespace='/notification')
                        exit(0)
                    break

        if not set_flooded:
            flooded = True
            for land in prev_set.lands:
                for sensor in land.sensors:
                    if not sensor.float:
                        flooded = False
                        break
                if not flooded:
                    break
            if flooded:
                error_list = run_valves(socket_io, current_set, prev_set)
                if error_list:
                    socket_io.emit('error_push', {'error_list': error_list}, namespace='/notification')
                    exit(0)
                set_flooded = True

        if not set_flooded and not land_flooded:
            pass
        # TODO check when to move to the next set


def run_valves(socket_io, current_set, prev_set):
    max_time = max([get_max_sensors_delay(land.sensors) for land in prev_set])
    time.sleep(max_time)

    def open_to_run():
        # open all valves to run in the current set
        # close all valves in the prev set

        for land in current_set.lands:
            for valve in land.valves:
                valve_config = next(filter(lambda x: x.config.active is True, valve.valve_configs), None)
                send_valve_position(valve, valve_config.run, socket_io)

        error_list = validate_move_valves(current_set.lands, 'run')
        if error_list:
            return error_list

        for land in prev_set.lands:
            for valve in land.valves:
                send_valve_position(valve, 0, socket_io)

    error_que = Queue()
    t = AppContextThread(target=lambda q: error_que.put(open_to_run()), args=(error_que,))
    t.start()
    t.join()
    if not error_que.empty():
        return error_que.get()


def validate_move_valves(lands, action_type):
    # checking the Moving and Idle position
    temp_check = {'moving': set(), 'idle': set()}

    # split into MOVING and IDLE
    # MOVING 5 sec
    # IDLE 30 sec
    # STOP EVERYTHING if no response in this time
    valves_num = 0
    i = 0
    while i < current_app.config.get("MOVING_TIME"):
        for land in lands:
            land_valves = Valve.query.filter_by(land_id=land.id).all()
            valves_num += len(land_valves)
            for valve in land_valves:
                if valve.status == 'Moving':
                    temp_check['moving'].add(valve.id)

        if len(temp_check['moving']) == valves_num:
            break

        time.sleep(1)
        i += 1

    error_list = []
    if len(temp_check['moving']) < valves_num:
        for land in lands:
            land_valves = Valve.query.filter_by(land_id=land.id).all()
            for valve in land_valves:
                if valve.id not in temp_check['moving']:
                    error_list.append(f"Valve {valve.name} failed to respond with MOVING status!")

    if error_list:
        return error_list

    # if gets here, that means all the valves have sent MOVING
    i = 0
    while i < current_app.config.get("IDLE_TIME"):
        for land in lands:
            land_valves = Valve.query.filter_by(land_id=land.id).all()
            for valve in land_valves:
                if valve.status == 'Idle':
                    temp_check['idle'].add(valve.id)

        if len(temp_check['idle']) == valves_num:
            break

        time.sleep(1)
        i += 1

    if len(temp_check['idle']) < valves_num:
        for land in lands:
            land_valves = Valve.query.filter_by(land_id=land.id).all()
            for valve in land_valves:
                if valve.id not in temp_check['idle']:
                    error_list.append(f"Valve {valve.name} failed to respond with IDLE status!")

    if error_list:
        return error_list

    # Check if the preflow/run == current_position ( +-1% error)
    for land in lands:
        land_valves = Valve.query.filter_by(land_id=land.id).all()
        for valve in land_valves:
            valve_config = next(filter(lambda x: x.config.active is True, valve.valve_configs), None)
            if action_type == 'preflow':
                if abs(valve.actuator_position - valve_config.preflow) > 1:
                    error_list.append(
                        f"Valve {valve.name} current-position does not correspond with the preflow position")
            if action_type == 'run':
                if abs(valve.actuator_position - valve_config.run) > 1:
                    error_list.append(
                        f"Valve {valve.name} current-position does not correspond with the run position")

    if error_list:
        return error_list


def preflow_valves(socket_io, current_set, sensors, prev_land):
    """
    :param sensors: sensors from current lands
    :param current_set: current set that needs to open all valves to preflow
    :param socket_io: socket communicator
    :param prev_land: land from prev set that needs to close the valves
    :return: None
    """

    max_time = get_max_sensors_delay(sensors)
    time.sleep(max_time)

    def open_to_preflow():
        # open all valves to preflow in the current set
        # then close all valves in the current land (that belongs to the prev_set)

        for land in current_set.lands:
            for valve in land.valves:
                valve_config = next(filter(lambda x: x.config.active is True, valve.valve_configs), None)
                send_valve_position(valve, valve_config.preflow, socket_io)

        error_list = validate_move_valves(current_set.lands, 'preflow')
        if error_list:
            return error_list

        for valve in prev_land.lands:
            send_valve_position(valve, 0, socket_io)

    error_que = Queue()
    t = AppContextThread(target=lambda q: error_que.put(open_to_preflow()), args=(error_que,))
    t.start()
    t.join()
    if not error_que.empty():
        return error_que.get()


def send_valve_position(valve, position, socket_io):
    # local_device = current_app.config.get("CACHE")['device']
    # remote_device = RemoteXBeeDevice(local_device, XBee64BitAddress.from_hex_string(valve.address))
    local_device = Device()
    remote_device = RemoteDevice(local_device, valve.address)

    try:
        local_device.send_data(remote_device, position)
    except Exception:
        traceback.print_exc()
        try:
            local_device.send_data(remote_device, position)
        except Exception:
            traceback.print_exc()
            message = f'Failed to move twice the valve: {valve.name} to position: {position}%!'
            error = Error(message=message)
            db.session.add(error)
            db.session.commit()
            socket_io.emit('error_push', {'id': valve.id, 'message': message}, namespace='/notification')


def get_max_sensors_delay(sensors):
    max_time = 0
    for sensor in sensors:
        current_time = datetime.datetime.now().replace(microsecond=0)
        sensor_config = next(filter(lambda x: x.config.active is True, sensors.sensor_configs), None)
        delta = current_time - sensor.trip_time
        delay_time = delta.seconds - sensor_config.delay * 60
        if 0 > delay_time > max_time:
            # haven't expired yet
            max_time = delay_time
    return max_time


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
