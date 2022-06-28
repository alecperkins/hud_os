import logging
import os
import json
from .helpers import getNow
from .sun import fetchSun
from .forecast import fetchForecast
from .nyct import fetchNYCSubwayStatus, fetchNYCSubwayRealTime
from datetime import datetime, timedelta

CACHE_DIR = os.path.join(os.getcwd(),'.cache')
if not os.path.exists(CACHE_DIR):
    os.mkdir(CACHE_DIR)

def _loadCacheable(key, fetcherFn, max_age_s=0):
    cache_filepath = os.path.join(CACHE_DIR, f'{key}.json')
    cached = None
    logging.debug(f'_loadCacheable key={key} max_age_s={max_age_s}')
    try:
        with open(cache_filepath) as f:
            cached = json.load(f)
    except Exception:
        logging.debug(f'_loadCacheable error loading cache key={key}')
    max_age = timedelta(seconds=max_age_s)
    now = datetime.utcnow()
    if not cached or now - datetime.fromtimestamp(cached.get('ts',0)) > max_age:
        logging.debug(f'_loadCacheable executing fetch key={key}')
        data = fetcherFn()
        logging.debug(f'_loadCacheable caching data key={key}')
        with open(cache_filepath, 'w') as f:
            json.dump({ 'data': data, 'ts': now.timestamp() }, f)
    else:
        logging.debug(f'_loadCacheable using cached key={key}')
        data = cached['data']
    return data

def loadAll():
    start_t = getNow()
    logging.debug(f'loadAll.start timestamp={start_t.isoformat()}')

    data = {}
    data['forecast'] = _loadCacheable('forecast', fetchForecast, max_age_s=(60 * 5))
    data['sun'] = _loadCacheable('sun', fetchSun, max_age_s=60)
    data['subway_realtime'] = _loadCacheable('subway_realtime', fetchNYCSubwayRealTime, max_age_s=(60 * 0.75))
    # data['subway_status'] = _loadCacheable('subway_status', fetchNYCSubwayStatus, max_age_s=(60 * 5))

    end_t = getNow()
    logging.debug(f'loadAll.success timestamp={end_t.isoformat()} duration_s={(end_t - start_t).total_seconds()}')
    return data
