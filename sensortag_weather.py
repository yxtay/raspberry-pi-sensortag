from __future__ import print_function

import datetime
import sys
import time

from bluepy.sensortag import SensorTag
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SENSORTAG_ADDRESS = "24:71:89:E6:AD:84"
GDOCS_OAUTH_JSON = "raspberry-pi-sensortag-97386df66227.json"
GDOCS_SPREADSHEET_NAME = "raspberry-pi-sensortag"
FREQUENCY_SECONDS = 60


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

    # Some sensors (e.g., temperature, accelerometer) need some time for initialization.
    # Not waiting here after enabling a sensor, the first read value might be empty or incorrect.
    time.sleep(1.0)


def get_readings(tag):
    try:
        # IR sensor
        ir_temp, ir = tag.IRtemperature.read()
        # humidity sensor
        humidty_temp, humidity = tag.humidity.read()
        # barometer
        baro_temp, pressure = tag.barometer.read()
        # lightmeter
        light = tag.lightmeter.read()
        # battery
        # readings["battery"] = tag.battery.read()

        readings = {"ir_temp": round(ir_temp, 2), "ir": round(ir, 2),
                    "humidity_temp": round(humidty_temp, 2), "humidity": round(humidity, 2),
                    "baro_temp": round(baro_temp, 2), "pressure": round(pressure, 2),
                    "light": round(light, 2)}
        return readings
    except Exception as e:
        print("Unable to take sensor readings.")
        print(e)
        return {}


def reconnect(tag):
    try:
        tag.connect(tag.deviceAddr, tag.addrType)
        enable_sensors(tag)
    except Exception as e:
        print("Unable to reconnect to SensorTag.")
        print(e)
        sys.exit(1)


def login_open_sheet(oauth_key_file, spreadsheet):
    """Connect to Google Docs spreadsheet and return the first worksheet."""
    try:
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(oauth_key_file, scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open(spreadsheet).sheet1
        return worksheet
    except Exception as e:
        print('Unable to login and get spreadsheet. '
              'Check OAuth credentials, spreadsheet name, '
              'and make sure spreadsheet is shared to the '
              'client_email address in the OAuth .json file!')
        print('Google sheet login failed with error:', e)
        sys.exit(1)


def append_readings(worksheet, readings):
    # Append the data in the spreadsheet, including a timestamp
    try:
        worksheet.append_row((datetime.datetime.now(),
                              readings["ir_temp"], readings["ir"],
                              readings["humidity_temp"], readings["humidity"],
                              readings["baro_temp"], readings["pressure"],
                              readings["light"]))
        print("Wrote a row to {0}".format(GDOCS_SPREADSHEET_NAME))
        return worksheet
    except Exception as e:
        # Error appending data, most likely because credentials are stale.
        # Null out the worksheet so a login is performed at the top of the loop.
        print("Append error, logging in again")
        print(e)
        return None


def main():
    # connect to sensortag
    print('Connecting to ' + SENSORTAG_ADDRESS)
    tag = SensorTag(SENSORTAG_ADDRESS)

    # enable sensors
    enable_sensors(tag)

    print('Logging sensor measurements to {0} every {1} seconds.'.format(GDOCS_SPREADSHEET_NAME, FREQUENCY_SECONDS))
    print('Press Ctrl-C to quit.')
    worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME)
    while True:
        # get sensor readings
        readings = get_readings(tag)
        if not readings:
            print("SensorTag disconnected. Reconnecting.")
            reconnect(tag)
            continue

        # print readings
        print("IR temperature:\t{}, reading:\t{}".format(readings["ir_temp"], readings["ir"]))
        print("Humidity temperature:\t{}, reading:\t{}".format(readings["humidity_temp"], readings["humidity"]))
        print("Barometer temperature:\t{}, reading:\t{}".format(readings["baro_temp"], readings["pressure"]))
        print("Light:\t{}".format(readings["light"]))

        worksheet = append_readings(worksheet, readings)
        # login if necessary.
        if worksheet is None:
            worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME)
            continue

        print()
        try:
            tag.waitForNotifications(FREQUENCY_SECONDS)
        except Exception as e:
            print(e)


    tag.disconnect()
    del tag

if __name__ == "__main__":
    main()
