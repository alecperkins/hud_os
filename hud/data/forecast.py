import requests
import logging
from hud import settings
from datetime import datetime
import pytz

def fetchForecast ():
    if not settings.WEATHERKIT_TOKEN:
        logging.warning('No WEATHERKIT_TOKEN configured!')
        return None
    forecast_endpoint = f'https://weatherkit.apple.com/api/v1/weather/en/{settings.LATITUDE}/{settings.LONGITUDE}'
    logging.debug('fetchForecast.request.call')
    r = requests.get(forecast_endpoint, params={
        'country': 'US',
        'dataSets': 'currentWeather',#forecastHourly',
        # 'exclude': 'minutely,daily,flags',
    }, headers={
      'Authorization': f"Bearer {settings.WEATHERKIT_TOKEN}",
      "Content-Type": "application/json",
    })
    if r.status_code != 200:
        logging.error(f'fetchForecast.request.error: {r.status_code}')
        return None
    logging.debug('fetchForecast.request.success')
    try:
        logging.debug('fetchForecast.parse.call')
        data = parse(r.json())
        logging.debug('fetchForecast.parse.success')
        return data
    except Exception as e:
        logging.error('fetchForecast.parse.error')
        logging.error(e)
        return None

def parse (raw_data):
    currently = raw_data.get('currentWeather')
    # hourly = raw_data.get('forecastHourly')

    current_temp_c = currently.get('temperature')
    feel_temp_c = currently.get('temperatureApparent')
    humidity = currently.get('humidity')
    wind_speed_mps = currently.get('windSpeed')
    wind_bearing_deg = currently.get('windDirection')
    wind_gust_mps = currently.get('windGust')
    
    summary = currently.get('conditionCode')
    icon = currently.get('conditionCode')
    hourly_forecast = [] # list(map(lambda x: { 'temp_f': x.get('temperature'), 'icon': x.get('icon'), 'time': datetime.fromtimestamp(x.get('time')).replace(tzinfo=pytz.utc).isoformat() }, hourly.get('hours',[])))

    return {
        'summary': summary,
        'icon': icon,
        # 'as_of_datetime': as_of_datetime,
        'hourly_forecast': hourly_forecast,
        'current_temp_f': cToF(current_temp_c),
        'feel_temp_f': cToF(feel_temp_c),
        'humidity': humidity,
        'wind_speed_mph': mpsToMph(wind_speed_mps),
        'wind_gust_mph': mpsToMph(wind_gust_mps),
        'wind_bearing_deg': wind_bearing_deg,
    }

def cToF(t_c):
  return t_c * 9.0 / 5.0 + 32.0

def mpsToMph(vel):
  return vel * 2.2369362921
