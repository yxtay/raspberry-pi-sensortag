from __future__ import print_function

import datetime
import sys
import time

from bluepy.btle import BTLEException
from bluepy.sensortag import SensorTag
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# configurations to be set accordingly
SENSORTAG_ADDRESS = "24:71:89:E6:AD:84"
GDOCS_OAUTH_JSON = "raspberry-pi-sensortag-97386df66227.json"
GDOCS_SPREADSHEET_NAME = "raspberry-pi-sensortag"
GDOCS_WORKSHEET_NAME = "data"
FREQUENCY_SECONDS = 54.0  # it takes about 4-5 seconds to obtain readings and upload to google sheets


def enable_sensors(tag):
    """Enable sensors so that readings can be made."""
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

def disable_sensors(tag):
    """Disable sensors to improve battery life."""
    tag.IRtemperature.disable()
    tag.accelerometer.disable()
    tag.humidity.disable()
    tag.magnetometer.disable()
    tag.barometer.disable()
    tag.gyroscope.disable()
    tag.keypress.disable()
    tag.lightmeter.disable()
    # tag.battery.disable()


def get_readings(tag):
    """Get sensor readings and collate them in a dictionary."""
    try:
        enable_sensors(tag)
        readings = {}
        # IR sensor
        readings["ir_temp"], readings["ir"] = tag.IRtemperature.read()
        # humidity sensor
        readings["humidity_temp"], readings["humidity"] = tag.humidity.read()
        # barometer
        readings["baro_temp"], readings["pressure"] = tag.barometer.read()
        # luxmeter
        readings["light"] = tag.lightmeter.read()
        # battery
        # readings["battery"] = tag.battery.read()
        disable_sensors(tag)

        # round to 2 decimal places for all readings
        readings = {key: round(value, 2) for key, value in readings.items()}
        return readings

    except BTLEException as e:
        print("Unable to take sensor readings.")
        print(e)
        return {}


def reconnect(tag):
    try:
        tag.connect(tag.deviceAddr, tag.addrType)

    except Exception as e:
        print("Unable to reconnect to SensorTag.")
        raise e


def login_open_sheet(oauth_key_file, spreadsheet_name, worksheet_name):
    """Connect to Google Docs spreadsheet and return the first worksheet."""
    try:
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(oauth_key_file, scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open(spreadsheet_name).worksheet(worksheet_name)
        return worksheet

    except Exception as e:
        print('Unable to login and get spreadsheet. '
              'Check OAuth credentials, spreadsheet name, '
              'and make sure spreadsheet is shared to the '
              'client_email address in the OAuth .json file!')
        print('Google sheet login failed with error:', e)
        sys.exit(1)


def append_readings(worksheet, readings):
    """Append the data in the spreadsheet, including a timestamp."""
    try:
        # remove erroneous readings
        if (readings["humidity_temp"] < readings["ir_temp"] - 2 or
                    readings["humidity_temp"] > readings["ir_temp"] + 2):
            readings["humidity_temp"] = ''
        if readings["humidity"] < 1 or readings["humidity"] > 99:
            readings["humidity"] = ''

        columns = ["ir_temp", "humidity_temp", "baro_temp", "ir", "humidity", "pressure", "light"]
        worksheet.append_row([datetime.datetime.now()] + [readings.get(col, '') for col in columns])
        print("Wrote a row to {0}".format(GDOCS_SPREADSHEET_NAME))
        return worksheet

    except Exception as e:
        # Error appending data, most likely because credentials are stale.
        # Null out the worksheet so a login is performed.
        print("Append error, logging in again")
        print(e)
        return None


def main():
    print('Connecting to {}'.format(SENSORTAG_ADDRESS))
    tag = SensorTag(SENSORTAG_ADDRESS)
    worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME, GDOCS_WORKSHEET_NAME)

    print('Logging sensor measurements to {0} every {1} seconds.'.format(GDOCS_SPREADSHEET_NAME, FREQUENCY_SECONDS))
    print('Press Ctrl-C to quit.')
    while True:
        # get sensor readings
        readings = get_readings(tag)
        if not readings:
            print("SensorTag disconnected. Reconnecting.")
            reconnect(tag)
            continue

        # print readings
        print("Time:\t{}".format(datetime.datetime.now()))
        print("IR reading:\t\t{}, temperature:\t{}".format(readings["ir"], readings["ir_temp"]))
        print("Humidity reading:\t{}, temperature:\t{}".format(readings["humidity"], readings["humidity_temp"]))
        print("Barometer reading:\t{}, temperature:\t{}".format(readings["pressure"], readings["baro_temp"]))
        print("Luxmeter reading:\t{}".format(readings["light"]))

        worksheet = append_readings(worksheet, readings)
        # login if necessary.
        if worksheet is None:
            worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME, GDOCS_WORKSHEET_NAME)
            continue

        print()
        time.sleep(FREQUENCY_SECONDS)


if __name__ == "__main__":
    main()
