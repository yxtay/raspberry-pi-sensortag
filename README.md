# Raspberry Pi wireless weather station
Raspberry Pi wireless weather station with TI SensorTag CC2650STK connected via Bluetooth Low Energy.

This project was developed with Python 2.7 on Raspbian. 
It works on the Raspberry Pi 3 Model B, which includes a Bluetooth Low Energy receiver.
It requires the [TI SensorTag CC2650STK](http://www.ti.com/tool/CC2650STK).

The project is based on the 
[Mini Weather Station project on hackster.io](https://www.hackster.io/idreams/make-a-mini-weather-station-with-a-raspberry-pi-2-and-sense-447866)
adapted for the SensorTag.

## Setup

```bash
# clone the repository
git clone git@github.com:yxtay/raspberry-pi-sensortag.git
cd raspberry-pi-sensortag

# install dependencies
sudo apt install python-pip virtualenvwrapper libglib2.0-dev
mkvirtualenv sensortag  # OPTIONAL: create virtualenv
pip install -r requirements.txt
```

## Configuration

Please set the following variables at the top of `sensortag_weather.py` as described.

### `SENSORTAG_ADDRESS`

The MAC address of the SensorTag can obtained by typing the following into the terminal.

```bash
sudo hcitool lescan
```

Turn on the SensorTag. You should see:

```bash
24:71:89:E6:AD:84 CC2650 SensorTag
```

Set `SENSORTAG_ADDRESS` accordingly.

### `GDOCS_OAUTH_JSON`

Follow the [`gspread` documentation instructions to obtain OAuth2 credentials from Google Developers Console](http://gspread.readthedocs.io/en/latest/oauth2.html).

Set `GDOCS_OAUTH_JSON` to the name of the file.

Open up the credentials file and note the email address under `client_email`, which is required in the next section.

### `GDOCS_SPREADSHEET_NAME` and `GDOCS_WORKSHEET_NAME`

Create a Google Spreadsheet and name it as you desire. Set `GDOCS_SPREADSHEET_NAME` to the name of the spreadsheet.

Rename the worksheet as you desire. Otherwise, it shall be "Sheet1" by default. Set `GDOCS_WORKSHEET_NAME` to the name of the worksheet.

Share the spreadsheet with `client_email` in the credential file from the previous section.

### `FREQUENCY_SECONDS`

It takes about 5-6 seconds to obtain readings from the SensorTag and upload them to Google Spreadsheet.
For approximiately per minute readings, set `FREQUENCY_SECONDS` to 55.

## Run script

```bash
workon sensortag  # activate virtualenv
python sensortag_weather.py
```
