from flask import current_app
import serial
import time
from gpiozero import CPUTemperature
from utils import mock_battery_temp
from email_service import send_email


def update_battery_temp(socket_io):
    battery_notified = False
    cpu_temp_notified = False

    min_battery_val = current_app.config.get("SYSTEM_BATTERY_MIN_VOLTAGE")
    cpu_max_temp = current_app.config.get("SYSTEM_CPU_MAX_TEMPERATURE")

    while True:
        with serial.Serial(current_app.config.get("MAIN_SYSTEM_DEVICE_PORT"), 9600, timeout=3) as ser:
            data = ser.read(8)
            data = data.decode()
            if data:
                message = data.split(',')

                battery = int(message[0]) / 10
                temperature = int(message[1]) / 10
                cpu = CPUTemperature()
                cpu_temperature = round(cpu.temperature * 1.8 + 32, 2)  # Convert to Deg F

                if battery < min_battery_val:
                    if not battery_notified:
                        send_email(current_app.config.get("SYSTEM_BATTERY_MESSAGE"))
                        battery_notified = True
                else:
                    if battery + 1.5 > min_battery_val:
                        battery_notified = False

                if cpu_temperature > cpu_max_temp:
                    if not cpu_temp_notified:
                        send_email(current_app.config.get("SYSTEM_CPU_TEMPERATURE_MESSAGE"))
                        cpu_temp_notified = True
                else:
                    if cpu_temperature < cpu_max_temp - 5:
                        cpu_temp_notified = False

                socket_io.emit('batteryTemp',
                               {'battery': battery, 'temperature': temperature, 'cpu_temperature': cpu_temperature},
                               namespace='/notification')


def update_battery_temp_test(socket_io):
    battery_notified = False
    cpu_temp_notified = False

    min_battery_val = current_app.config.get("SYSTEM_BATTERY_MIN_VOLTAGE")
    cpu_max_temp = current_app.config.get("SYSTEM_CPU_MAX_TEMPERATURE")

    while True:
        time.sleep(5)
        message = mock_battery_temp()
        message = message.split(',')

        battery = int(message[0]) / 10
        temperature = int(message[1]) / 10
        cpu_temperature = int(message[2]) / 10

        if battery < min_battery_val:
            if not battery_notified:
                send_email(current_app.config.get("SYSTEM_BATTERY_MESSAGE"))
                battery_notified = True
        else:
            if battery + 1.5 > min_battery_val:
                battery_notified = False

        if cpu_temperature > cpu_max_temp:
            if not cpu_temp_notified:
                send_email(current_app.config.get("SYSTEM_CPU_TEMPERATURE_MESSAGE"))
                cpu_temp_notified = True
        else:
            if cpu_temperature < cpu_max_temp - 5:
                cpu_temp_notified = False

        socket_io.emit('batteryTemp',
                       {'battery': battery, 'temperature': temperature, 'cpu_temperature': cpu_temperature},
                       namespace='/notification')


def get_gps_data_test():
    pass


def get_gps_data():
    moving_email_sent = False
    stopped_email_sent = True

    while True:
        with serial.Serial(current_app.config.get("GPS_SERIAL_PORT"), 9600) as ser:
            data = ser.read(67)
            data = data.decode()
            if data:
                message = data.split(',')
                if 'A' not in message:
                    continue
                n_s_indication = message[4]
                latitude = format_coordinates(message[3], n_s_indication)
                w_e_indication = message[6]
                longitude = format_coordinates(message[5], w_e_indication)
                speed = int(message[7])
                map_url = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"

                if speed >= current_app.config.get("GROUND_SPEED_MIN"):
                    if not moving_email_sent:
                        send_email(current_app.config.get("UNIT_IN_MOTION_MESSAGE"))
                        moving_email_sent = True
                        stopped_email_sent = False
                else:
                    if not stopped_email_sent:
                        send_email(current_app.config.get("UNIT_STOPPED_MESSAGE") + map_url)
                        stopped_email_sent = True
                        moving_email_sent = False

                time.sleep(30)


def format_coordinates(coords, direction):
    degrees_min = coords.split('.')[0]
    degrees = int(degrees_min[:len(degrees_min) - 2])
    minutes = int(degrees_min[-2:])
    min_decimals = float("0." + coords.split('.')[1])
    coords = degrees + (minutes + min_decimals) / 60

    if direction == 'S' or direction == 'W':
        return 0 - coords
    return coords
