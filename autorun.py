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
                # TODO open to run all the valves in the current set
                set_flooded = True

        if not set_flooded and not land_flooded:
            pass
        # TODO check when to move to the next set


def validation_open_valves(valves):
    pass


def run_valves(socket_io, current_set, prev_set):
    max_time = max([get_max_sensors_delay(land.sensors) for land in prev_set])

    def open_to_run():
        # open all valves to run in the current set
        # close all valves in the prev set

        time.sleep(max_time)

        for land in current_set.lands:
            for valve in land.valves:
                valve_config = next(filter(lambda x: x.config.active is True, valve.valve_configs), None)
                send_valve_position(valve, valve_config.run, socket_io)
                # TODO check for MOVING and IDLE status to confirm

        # TODO checks before

        for land in prev_set.lands:
            for valve in land.valves:
                send_valve_position(valve, 0, socket_io)

        # TODO CHECK when is done to move to the next set, global VAR

    t = AppContextThread(target=open_to_run)
    t.start()


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

        # checking the Moving and Idle position
        temp_check = {'moving': set(), 'idle': set()}
        i = 0
        valves_num = None
        while i < 5:
            prev_land_valves = Valve.query.filter_by(land_id=prev_land.id).all()
            valves_num = len(prev_land_valves)
            for valve in prev_land_valves:
                if valve.status == 'Moving':
                    temp_check['moving'].add(valve.id)
                if valve.status == 'Idle':
                    temp_check['idle'].add(valve.id)

            if len(temp_check['moving']) == valves_num and len(temp_check['idle']) == valves_num:
                break

            # wait for Moving and Idle status 5 * 60 sec.
            time.sleep(60)
            i += 1

        error_list = []
        if len(temp_check['moving']) < valves_num:
            prev_land_valves = Valve.query.filter_by(land_id=prev_land.id).all()
            # TODO if it gets here, then not all the valves responded in the specific time, return an error
            for valve in prev_land_valves:
                if valve.id not in temp_check['moving']:
                    error_list.append(f"Valve {valve.name} failed to respond with MOVING status!")

        if len(temp_check['idle']) < valves_num:
            prev_land_valves = Valve.query.filter_by(land_id=prev_land.id).all()
            for valve in prev_land_valves:
                if valve.id not in temp_check['idle']:
                    error_list.append(f"Valve {valve.name} failed to respond with IDLE status!")

        if error_list:
            return error_list

        # Check id the preflow == current_position ( +-1% error)
        prev_land_valves = Valve.query.filter_by(land_id=prev_land.id).all()
        for valve in prev_land_valves:
            valve_config = next(filter(lambda x: x.config.active is True, valve.valve_configs), None)
            if abs(valve.actuator_position - valve_config.preflow) > 1:
                error_list.append(f"Valve {valve.name} current-position does not correspond with the preflow position")

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
