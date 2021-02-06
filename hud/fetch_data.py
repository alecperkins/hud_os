import os
import requests
import json
from datetime import datetime, date, timedelta, timezone


from dotenv import load_dotenv

load_dotenv()

DARKSKY_API_KEY = os.environ.get('DARKSKY_API_KEY')
MTA_REALTIME_API_KEY = os.environ.get('MTA_REALTIME_API_KEY')

LAT = 40.8251054
LON = -73.9410159

def cToF (c_val):
    return c_val * 9.0 / 5.0 + 32

def getNow ():
    return datetime.fromisoformat(datetime.utcnow().isoformat() + '-00:00')

def fetchSun ():
    endpoint = f'https://api.sunrise-sunset.org/json?lat={LAT}&lng={LON}&formatted=0'
    def _getSun (d):
        r = requests.get(endpoint, params={
            'date': d.isoformat(),
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
        print(today_sunset < now, today_sunset, now)
        if today_sunset < now:
            data = _getSun(today + timedelta(days=1))
    if data:
        sunrise = datetime.fromisoformat(data['sunrise'])
        sunset = datetime.fromisoformat(data['sunset'])
        if now < sunrise:
            return { 'next': 'sunrise', 'time': sunrise.isoformat() }
        return { 'next': 'sunset', 'time': sunset.isoformat() }
    return None

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


def fetchWeather ():
    forecast_endpoint = f'https://api.darksky.net/forecast/{DARKSKY_API_KEY}/{LAT},{LON}'
    r = requests.get(forecast_endpoint, params={
        'units': 'us',
        'exclude': 'minutely,daily,flags',
    })
    r.raise_for_status()
    return parseWeather(r.json())

def parseWeather (raw_data):
    # as_of_datetime = datetime.fromtimestamp(raw_data.get('time'))
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
    hourly_forecast = list(map(lambda x: { 'temp_f': x.get('temperature'), 'icon': x.get('icon'), 'time': datetime.fromtimestamp(x.get('time')).isoformat() }, hourly.get('data',[])))

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

def fetchNYCSubwayTurnstile ():
    # http://web.mta.info/developers/turnstile.html
    """
    C/A      = Control Area (A002)
    UNIT     = Remote Unit for a station (R051)
    SCP      = Subunit Channel Position represents an specific address for a device (02-00-00)
    STATION  = Represents the station name the device is located at
    LINENAME = Represents all train lines that can be boarded at this station
            Normally lines are represented by one character.  LINENAME 456NQR repersents train server for 4, 5, 6, N, Q, and R trains.
    DIVISION = Represents the Line originally the station belonged to BMT, IRT, or IND   
    DATE     = Represents the date (MM-DD-YY)
    TIME     = Represents the time (hh:mm:ss) for a scheduled audit event
    DESc     = Represent the "REGULAR" scheduled audit event (Normally occurs every 4 hours)
            1. Audits may occur more that 4 hours due to planning, or troubleshooting activities. 
            2. Additionally, there may be a "RECOVR AUD" entry: This refers to a missed audit that was recovered. 
    ENTRIES  = The comulative entry register value for a device
    EXIST    = The cumulative exit register value for a device
    """
    return {}

FEED_LINE_MAPPING = {
    # These feeds include others but only mapping the ones of interest
    'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace': ['A','C'],
    'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm': ['B','D'],
    'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs': ['3'],
}
# Each "stop" is a platform at a station
LINE_STOP_MAPPING = {
    '3': '301S', # Harlem - 148 (southbound)
    'A': 'A12S',# 145 (southbound)
    'B': 'D13S',
    'C': 'A12S',
    'D': 'D13S',
}
 # 
# 302S # 145 (southbound)
from underground import SubwayFeed
# https://pypi.org/project/underground/
def fetchNYCSubwayRealTime ():
    times = []
    for feed_url, lines in FEED_LINE_MAPPING.items():
        feed = SubwayFeed.get(feed_url, api_key=MTA_REALTIME_API_KEY)
        stops = feed.extract_stop_dict()
        for line_name in lines:
            print(line_name, stops.keys())
            line = stops.get(line_name) # The line may not be stopping at this stop currently
            if line:
                print(line_name, line.keys())
                for time in line.get(LINE_STOP_MAPPING[line_name],[]):
                    times.append({
                        'line': line_name,
                        'direction': 'S', # hardcoding southbound
                        'time': time.timestamp(),
                    })
    return times
    # https://developers.google.com/transit/gtfs-realtime/
    # https://api.mta.info/#/landing
    # https://api.mta.info/#/HelpDocument

from xmljson import badgerfish as bf
from defusedxml.ElementTree import fromstring
TARGET_LINES = ['MTA NYCT_3','MTA NYCT_A','MTA NYCT_B','MTA NYCT_D','MTA NYCT_C']
def _tag (s):
    return '{http://www.siri.org.uk/siri}' + s
def _get (t, p):
    while len(p) > 0 and hasattr(t,'keys'):
        # if hasattr(t,'keys'):
        #     print(t.keys(), p[0])
        # else:
        #     print(t, p[0])
        k = p.pop(0)
        if k != '$':
            k = _tag(k)
        t = t[k]
    return t
def fetchNYCSubwayStatus ():
    endpoint = 'http://web.mta.info/status/ServiceStatusSubway.xml'
    r = requests.get(endpoint)
    str_data = None
    if r.status_code == 200:
        str_data = r.content
    relevant = []
    if str_data:
        tree = fromstring(str_data)
        data = bf.data(tree)
        situations = _get(data, ['Siri','ServiceDelivery','SituationExchangeDelivery','Situations','PtSituationElement'])
        # # print(dir(situations))
        for situation in situations:
            # print(_get(situation,['SituationNumber','$']))
            lines = _get(situation, ['Affects','VehicleJourneys','AffectedVehicleJourney'])
            for line in lines:
                line_name = _get(line, ['LineRef','$']).strip()
                if line_name in TARGET_LINES:
                    summary = _get(situation,['Summary','$'])
                    if summary != 'Weekend Service' and summary != 'No Scheduled Service' and not 'do not run on weekends' in summary:
                        relevant.append({
                            'line': line_name[-1],
                            'summary': summary,
                        })
    return relevant
    """
    from fetch_data import fetchNYCSubwayStatus, _get, _tag
    data = fetchNYCSubwayStatus()
    """

"""
[{'line': 'D', 'direction': 'S', 'time': datetime.datetime(2021, 1, 31, 22, 11, 24, tzinfo=<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>)}, {'line': '3', 'direction': 'S', 'time': datetime.datetime(2021, 1, 31, 22, 12, 30, tzinfo=<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>)}, {'line': 'C', 'direction': 'S', 'time': datetime.datetime(2021, 1, 31, 22, 13, 30, tzinfo=<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>)}, {'line': 'A', 'direction': 'S', 'time': datetime.datetime(2021, 1, 31, 22, 14, 24, tzinfo=<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>)}, {'line': 'A', 'direction': 'S', 'time': datetime.datetime(2021, 1, 31, 22, 26, tzinfo=<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>)}, {'line': 'D', 'direction': 'S', 'time': datetime.datetime(2021, 1, 31, 22, 27, 30, tzinfo=<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>)}, {'line': '3', 'direction': 'S', 'time': datetime.datetime(2021, 1, 31, 22, 29, 30, tzinfo=<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>)}, {'line': 'A', 'direction': 'S', 'time': datetime.datetime(2021, 1, 31, 22, 33, tzinfo=<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>)}, {'line': 'D', 'direction': 'S', 'time': datetime.datetime(2021, 1, 31, 22, 39, 30, tzinfo=<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>)}, {'line': 'A', 'direction': 'S', 'time': datetime.datetime(2021, 1, 31, 22, 43, tzinfo=<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>)}, {'line': 'D', 'direction': 'S', 'time': datetime.datetime(2021, 1, 31, 22, 51, 30, tzinfo=<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>)}, {'line': 'A', 'direction': 'S', 'time': datetime.datetime(2021, 1, 31, 23, 1, tzinfo=<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>)}, {'line': 'D', 'direction': 'S', 'time': datetime.datetime(2021, 1, 31, 23, 3, 30, tzinfo=<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>)}, {'line': 'D', 'direction': 'S', 'time': datetime.datetime(2021, 1, 31, 23, 15, 30, tzinfo=<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>)}, {'line': 'A', 'direction': 'S', 'time': datetime.datetime(2021, 1, 31, 23, 19, 20, tzinfo=<DstTzInfo 'US/Eastern' EST-1 day, 19:00:00 STD>)}]
"""

"""
[{'line': '3', 'summary': 'Weekend Service'}, {'line': '3', 'summary': 'Weekend Service'}, {'line': 'A', 'summary': 'Weekend Service'}, {'line': 'A', 'summary': 'Weekend Service'}, {'line': 'B', 'summary': 'No Scheduled Service'}, {'line': 'B', 'summary': 'No Scheduled Service'}, {'line': 'C', 'summary': 'Weekend Service'}, {'line': 'C', 'summary': 'Weekend Service'}, {'line': 'D', 'summary': 'Weekend Service'}, {'line': 'D', 'summary': 'Weekend Service'}, {'line': 'B', 'summary': '[B] trains do not run on weekends. Please use   MYmta   to plan your trip.'}, {'line': 'B', 'summary': '[B] trains do not run on weekends. Please use   MYmta   to plan your trip.'}]
"""


# def fetchNYCSubwaySchedule ():
#     endpoint = 'http://web.mta.info/developers/data/nyct/subway/google_transit.zip'
#     # unzip


# def fetchSensorPush ():
#     sensorpush.



def fetchAll ():
    # TODO: try/except each of these
    weather = fetchWeather()
    sun = fetchSun()
    subway_realtime = fetchNYCSubwayRealTime()
    subway_status = fetchNYCSubwayStatus()
    return {
        'weather': weather,
        'sun': sun,
        'subway_realtime': subway_realtime,
        'subway_status': subway_status,
    }



CACHE_DIR = os.path.join(os.path.dirname(__file__),'.datacache')
if not os.path.exists(CACHE_DIR):
    os.mkdir(CACHE_DIR)

def loadOrFetchData (max_age_min=5):
    cache_file = os.path.join(CACHE_DIR, 'cache.json')
    cache = None
    try:
        with open(cache_file) as f:
            cache = json.load(f)
    except:
        pass
    if cache and 'ts' in cache and (datetime.now() - datetime.fromtimestamp(cache['ts'])) < timedelta(minutes=max_age_min):
        return cache['data']
    
    data = fetchAll()
    with open(cache_file, 'w') as f:
        json.dump({
            'data': data,
            'ts': datetime.now().timestamp(),
        }, f)
    return data


# cache data to ./.datacache
# fetch if older than 5 minutes
# adjust frequency based on time of day

