
"""
{
      "results":
      {
        "sunrise":"2015-05-21T05:05:35+00:00",
        "sunset":"2015-05-21T19:22:59+00:00",
        "solar_noon":"2015-05-21T12:14:17+00:00",
        "day_length":51444,
        "civil_twilight_begin":"2015-05-21T04:36:17+00:00",
        "civil_twilight_end":"2015-05-21T19:52:17+00:00",
        "nautical_twilight_begin":"2015-05-21T04:00:13+00:00",
        "nautical_twilight_end":"2015-05-21T20:28:21+00:00",
        "astronomical_twilight_begin":"2015-05-21T03:20:49+00:00",
        "astronomical_twilight_end":"2015-05-21T21:07:45+00:00"
      },
       "status":"OK"
    }
"""


import os
import requests
import json
from datetime import datetime, date, timedelta, timezone

from hud import settings
from .helpers import getNow

def fetchSun ():
    endpoint = 'https://api.sunrise-sunset.org/json'
    def _getSun (d):
        r = requests.get(endpoint, params={
            'date': d.isoformat(),
            'lat': settings.LATITUDE,
            'lng': settings.LONGITUDE,
            'formatted': 0,
        })
        if r.status_code == 200:
            data = r.json()
            if data.get('status') == 'OK':
                return data.get('results')
        return None
    today = date.today()
    now = getNow()
    data = _getSun(today)
    if data:
        today_sunset = datetime.fromisoformat(data.get('sunset'))
        if today_sunset < now:
            data = _getSun(today + timedelta(days=1))
    if data:
        sunrise = datetime.fromisoformat(data['sunrise'])
        sunset = datetime.fromisoformat(data['sunset'])
        if now < sunrise:
            return { 'next': 'sunrise', 'time': sunrise.isoformat() }
        return { 'next': 'sunset', 'time': sunset.isoformat() }
    return None
