from bluepy.sensortag import SensorTag


def enable_sensors(tag):
    tag.IRtemperature.enable()
    tag.accelerometer.enable()
    tag.humidity.enable()
    tag.magnetometer.enable()
    tag.barometer.enable()
    tag.gyroscope.enable()
    tag.keypress.enable()
    tag.lightmeter.enable()
    # tag.battery.enable()


def get_readings(tag):
    readings = dict()
    # IR sensor
    readings["ir_temp"], readings["ir"] = tag.IRtemperature.read()
    # humidity sensor
    readings["humidty_temp"], readings["humidity"] = tag.humidity.enable()
    # barometer
    readings["baro_temp"], readings["pressure"] = tag.barometer.read()
    # lightmeter
    readings["light"] = tag.lightmeter.read()
    # battery
    # readings["battery"] = tag.battery.read()
    return readings


def main():
    from __future__ import print_function
    import time
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('host', action='store', help='MAC of BT device')
    arg = parser.parse_args(sys.argv[1:])

    # connect to sensortag
    print('Connecting to ' + arg.host)
    tag = SensorTag(arg.host)

    # enable sensors
    enable_sensors(tag)

    # Some sensors (e.g., temperature, accelerometer) need some time for initialization.
    # Not waiting here after enabling a sensor, the first read value might be empty or incorrect.
    time.sleep(1.0)

    readings = get_readings(tag)
    print(readings)

    tag.disconnect()
    del tag
