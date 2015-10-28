# -*- coding: utf-8 -*-
import config as settings

from flask.ext.script import Command, Option
from ..services import BoxApiService

import json
import requests
import Adafruit_DHT


class TemperatureHumidity(Command):
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
        device_id = BoxApiService.get_device_id()
        url = '%s%s' % (settings.CORE_SERVER_ENDPOINT, 'event/')
        # Try to grab a sensor reading.  Use the read_retry method which will retry up
        # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
        humidity, temperature = Adafruit_DHT.read_retry(kwargs.get('sensor'), kwargs.get('pin'))

        if humidity is not None and temperature is not None:

            data = json.dumps({"sensor_action": "temperature,humidity",
                               "temperature": temperature,
                               "humidity": humidity,
                               "tags": {
                                   "device_id": device_id,
                               }})

            resp = requests.post(url, data=data)
            print(resp.content)

        else:
            print('Failed to get reading. Try again!')
