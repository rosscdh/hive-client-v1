# -*- coding: utf-8 -*-
import config as settings

from flask.ext.script import Command, Option
from ..services import BoxApiService

import requests
import Adafruit_DHT


class TemperatureHumidity(Command):
    """
    Must be run as sudo

    # notice the virtualenv use of python
    sudo .venv/bin/python manage.py temperature_humidity -s :sensor -p :pin

    """
    option_list = (
        Option('--sensor', '-s',
               dest='sensor',
               default=11),
        Option('--pin', '-p',
               dest='pin',
               default=4),
    )

    def run(self, **kwargs):
        """
        """
        # Try to grab a sensor reading.  Use the read_retry method which will retry up
        # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
        sensor = kwargs.get('sensor')
        humidity, temperature = Adafruit_DHT.read_retry(sensor, kwargs.get('pin'))

        if humidity is not None and temperature is not None:

            device_id = BoxApiService.get_device_id()
            url = '%s%s' % (settings.CORE_SERVER_ENDPOINT, 'event/')

            data = {"sensor_action":
                    "temperature,humidity",
                    "temperature": temperature,
                    "humidity": humidity,
                    "tags": {
                        "device_id": device_id,
                        "sensor_id": device_id,
                    }}

            #
            # NB: MUST use json= here as we are expecting plain json payload at the api
            #
            resp = requests.post(url, json=data)
            print(resp.content)

        else:
            print('Failed to get reading humidity: %s, temperature: %s. Try again!' % (humidity, temperature))
