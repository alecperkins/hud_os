import logging
from hud import settings



from underground import SubwayFeed

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

# https://pypi.org/project/underground/
def fetchNYCSubwayRealTime ():
    if not settings.MTA_REALTIME_API_KEY:
        logging.warning('No META_REALTIME_API_KEY configured!')
        return []
    times = []
    for feed_url, lines in FEED_LINE_MAPPING.items():
        feed = SubwayFeed.get(feed_url, api_key=settings.MTA_REALTIME_API_KEY)
        stops = feed.extract_stop_dict()
        for line_name in lines:
            line = stops.get(line_name) # The line may not be stopping at this stop currently
            if line:
                for time in line.get(LINE_STOP_MAPPING[line_name],[]):
                    times.append({
                        'line': line_name,
                        'direction': 'S', # hardcoding southbound
                        'time': time.isoformat(),
                    })
    logging.debug(f'fetchNYCSubwayRealTime trains={len(times)}')
    return times


import requests
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
    logging.debug('fetchNYCSubwayStatus.request.call')
    r = requests.get(endpoint)
    str_data = None
    if r.status_code == 200:
        str_data = r.content
    else:
        logging.error(f'fetchNYCSubwayStatus.request.response.error {r.status_code}')
        return []
    logging.error('fetchNYCSubwayStatus.request.response.success')
    relevant = []
    situations = []
    if str_data:
        tree = fromstring(str_data)
        data = bf.data(tree)
        situations = _get(data, ['Siri','ServiceDelivery','SituationExchangeDelivery','Situations','PtSituationElement'])
        # # print(dir(situations))
        logging.debug(f'fetchNYCSubwayStatus situations={len(situations)}')
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
    logging.debug(f'fetchNYCSubwayStatus relevant={len(relevant)}')
    return relevant
