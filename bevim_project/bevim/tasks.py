from django.shortcuts import render
from bevim_project.settings import REST_BASE_URL
import datetime, threading, json 
import requests as api_requests

def get_sensors():
    url_to_rest = REST_BASE_URL + 'v1/sensor?format=json'
    api_response = api_requests.get(url_to_rest)
    time = threading.Timer(1, get_sensors)
    time.start()
    data = json.loads(api_response.content.decode('utf8'))

    if data:
    	time.cancel()