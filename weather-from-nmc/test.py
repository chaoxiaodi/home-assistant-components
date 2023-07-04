import requests
import json

def update(code):
    base_url = 'http://www.nmc.cn'
    real_uri = '/f/rest/real/%s' % code
    forcast_uri = '/rest/weather?stationid=%s' % code
    try:
        json_realtimetext = requests.get(base_url + real_uri, timeout=3).json()
        print(json_realtimetext['station'])
        # self._realtime_data = json.loads(json_realtimetext)

        json_forcasttext = requests.get(base_url + forcast_uri, timeout=3).json()
        print(json_forcasttext)
        # self._forecast_data = json.loads(json_forcasttext)

        json_airtext = requests.get(base_url + real_uri, timeout=3).json
        # self._air_data = json.loads(json_airtext)
    except Exception as e:
        print(e)

update(53892)