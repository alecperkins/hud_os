import requests
import logging
from hud import settings
from datetime import datetime
import pytz

def fetchForecast ():
    if not settings.DARKSKY_API_KEY:
        logging.warning('No DARKSKY_API_KEY configured!')
        return None
    forecast_endpoint = f'https://api.darksky.net/forecast/{settings.DARKSKY_API_KEY}/{settings.LATITUDE},{settings.LONGITUDE}'
    logging.debug('fetchForecast.request.call')
    r = requests.get(forecast_endpoint, params={
        'units': 'us',
        'exclude': 'minutely,daily,flags',
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
    currently = raw_data.get('currently')
    hourly = raw_data.get('hourly')

    current_temp_f = currently.get('temperature')
    feel_temp_f = currently.get('apparentTemperature')
    humidity = currently.get('humidity')
    wind_speed_mph = currently.get('windSpeed')
    wind_bearing_deg = currently.get('windBearing')
    wind_gust_mph = currently.get('windGust')
    
    summary = hourly.get('summary')
    icon = hourly.get('icon')
    hourly_forecast = list(map(lambda x: { 'temp_f': x.get('temperature'), 'icon': x.get('icon'), 'time': datetime.fromtimestamp(x.get('time')).replace(tzinfo=pytz.utc).isoformat() }, hourly.get('data',[])))

    return {
        'summary': summary,
        'icon': icon,
        # 'as_of_datetime': as_of_datetime,
        'hourly_forecast': hourly_forecast,
        'current_temp_f': current_temp_f,
        'feel_temp_f': feel_temp_f,
        'humidity': humidity,
        'wind_speed_mph': wind_speed_mph,
        'wind_gust_mph': wind_gust_mph,
        'wind_bearing_deg': wind_bearing_deg,
    }
