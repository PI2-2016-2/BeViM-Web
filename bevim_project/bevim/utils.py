from scipy import integrate

from django.db import connection, IntegrityError, transaction
import json
import requests as api_requests

from bevim.models import Experiment, Job, Sensor, Acceleration, Amplitude, Frequency, Speed
from bevim_project.settings import REST_BASE_URL
from django.db.models.signals import post_save
from django.core.serializers.json import DjangoJSONEncoder


# Util methods - Controller

class ExperimentUtils:

    def numerical_integration(y_array, x_array):
        return integrate.cumtrapz(y_array, x_array)

    def populate_database(experiment):
        jobs = experiment.job_set.all()
        if jobs:
            jobs_ids = []
            for job in jobs:
                jobs_ids.append(job.id)

            if jobs_ids:
                ExperimentUtils.save_data(jobs_ids, "acceleration", Acceleration)
                ExperimentUtils.save_data(jobs_ids, "frequency", Frequency)

    def save_data(experiment_data, data_class):
        first_job = None
        with transaction.atomic():
            for data in experiment_data:
                sensor = Sensor.objects.get(name=data[0])
                job = Job.objects.get(pk=data[5])
                first_job = job
                data_class.objects.create(sensor=sensor, x_value=data[1], y_value=data[2],
                                        z_value=data[3], timestamp=data[4], job=job)

        if first_job is not None:
            experiment = first_job.experiment
            return experiment

        return None


    def free_equipment(experiment_id):
        experiment = Experiment.objects.get(pk=experiment_id)
        experiment.active = False
        experiment.save()


    def get_experiment_result(experiment_id):
        jobs = Job.objects.filter(experiment=experiment_id)

        accelerations = []
        amplitudes = []
        frequencies = []
        speeds = []
    
        for job in jobs:
            job_accelerations = job.acceleration_set.all()
            if job_accelerations:
                job_amplitudes = job.amplitude_set.all()
                job_frequencies = job.frequency_set.all()
                job_speeds = job.speed_set.all()
                
                accelerations.append(job_accelerations)
                amplitudes.append(job_amplitudes)
                frequencies.append(job_frequencies)
                speeds.append(job_speeds)

        result = {
            'accelerations' : accelerations, 
            'amplitudes': amplitudes, 
            'frequencies': frequencies, 
            'speeds': speeds
        }
        return result

    def get_chart_data(result_data, chart_description, color):
        timestamps = ['x']
        data_values = [chart_description]
        for job_data in result_data:
            for data in job_data:
                timestamps.append(data.timestamp)
                data_values.append(data.z_value) # Get sensor data from axis z

        columns = [timestamps, data_values]
        chart_data = {
            'x' : 'x',
            'columns': columns,
            'colors': {chart_description: color}
            # 'type': 'spline'
        }
        
        chart_data = json.dumps(chart_data, cls=DjangoJSONEncoder)
        return chart_data

class RestUtils:

    TIMEOUT = 15 # In seconds

    @classmethod
    def post_to_rasp_server(cls, url, data, headers=None):
        url_to_rest = REST_BASE_URL + url
        if headers is None:
            headers = {'content-type': 'application/json'}
        response = api_requests.post(url_to_rest, data=json.dumps(data),
                        headers=headers, timeout=cls.TIMEOUT)
        return response

    @classmethod
    def put_to_rasp_server(cls, url, data, headers=None):
        url_to_rest = REST_BASE_URL + url
        if headers is None:
            headers = {'content-type': 'application/json'}
        response = api_requests.put(url_to_rest, data=json.dumps(data),
                        headers=headers, timeout=cls.TIMEOUT)
        return response

    @classmethod
    def get_from_rasp_server(cls, url):
        url_to_rest = REST_BASE_URL + url
        response = api_requests.get(url_to_rest)
        return response
