from flask import g
from digi.xbee.devices import RemoteXBeeDevice, XBee64BitAddress
import time


def sending():
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
