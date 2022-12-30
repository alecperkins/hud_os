
bradhurst_station_id = "4020"

"""
{
    "data": {
        "stations": [
            {
                "is_returning": 1,
                "legacy_id": "4020",
                "station_id": "4020",
                "num_bikes_disabled": 0,
                "num_docks_available": 21,
                "num_bikes_available": 1,
                "is_installed": 1,
                "is_renting": 1,
                "eightd_has_available_keys": false,
                "station_status": "active",
                "num_ebikes_available": 0,
                "last_reported": 1657383939,
                "num_docks_disabled": 0
            },
        ]
    }
}
"""

import requests

def fetchCitibike ():
    endpoint = 'https://gbfs.citibikenyc.com/gbfs/en/station_status.json'
    r = requests.get(endpoint)
    if r.status_code == 200:
        data = r.json().get('data')
        for station in data.get('stations', []):
            if station.get('station_id') == bradhurst_station_id:
                return station
    return None

