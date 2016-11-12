from django.shortcuts import render
import datetime, threading, json 
import requests as api_requests

from bevim_project.settings import REST_BASE_URL
from bevim.models import Experiment


def get_experiment_data(experiment_id):
    url_to_rest = REST_BASE_URL + 'v1/acceleration'
    api_response = api_requests.get(url_to_rest)
    
    experiment = Experiment.objects.get(pk=experiment_id)
    jobs = experiment.job_set.all()

    total_time = 0
    for job in jobs:
        total_time += job.job_time

    time = threading.Timer(total_time, get_experiment_data(experiment_id))
    if api_response:
        print ("TA AQUI")
        time.cancel()
        data = json.loads(api_response.content.decode('utf8'))

        if data:
            time.cancel()
            print (data)
            is_processing_data = False
        else:
            is_processing_data = True
    else:
        time.start()
        # time.cancel()
        is_processing_data = True       

    return is_processing_data