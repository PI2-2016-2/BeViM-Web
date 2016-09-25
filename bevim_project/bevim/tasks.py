import datetime, threading, json 
import requests as api_requests

def get_sensors():
    url_to_rest = 'http://127.0.0.1:8002/api/v1/sensor?format=json'
    response = api_requests.get(url_to_rest)
    time = threading.Timer(1, get_sensors)
    time.start()
    data = json.loads(response.content.decode('utf8'))
    if data:
    	time.cancel()

