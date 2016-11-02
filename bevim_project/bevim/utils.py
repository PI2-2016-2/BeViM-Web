from django.db import connection, IntegrityError, transaction
import json
import requests as api_requests

from bevim.models import Experiment, Job, Sensor, Acceleration, Amplitude, Frequency, Speed
from bevim_project.settings import REST_BASE_URL
from django.db.models.signals import post_save


# Util methods - Controller

class ExperimentUtils:

    def populate_database(experiment):
        jobs = experiment.job_set.all()
        if jobs:
            jobs_ids = []
            for job in jobs:
                jobs_ids.append(job.id)

            if jobs_ids:
                ExperimentUtils.save_data(jobs_ids, "acceleration", Acceleration)
                ExperimentUtils.save_data(jobs_ids, "frequency", Frequency)

    def save_data(jobs, data_type, data_class):
        experiment_data = ExperimentUtils.get_data_by_jobs(jobs, data_type)
        if experiment_data:
            with transaction.atomic():
                for data in experiment_data:
                    sensor_data = data['sensor']
                    sensor = Sensor.objects.get(name=sensor_data['name'])
                    job = Job.objects.get(pk=data['job_id'])
                    data_class.objects.create(sensor=sensor, x_value=data['x_value'], y_value=data['y_value'],
                                            z_value=data['z_value'], timestamp=data['timestamp_ref'], job=job)

    def get_data_by_jobs(jobs, data_type):
        response = RestUtils.get_from_rasp_server('v1/' + data_type)
        experiment_data = json.loads(response.content.decode('utf8'))

        data_jobs = []
        if experiment_data:
          for data in experiment_data:
            job_id = data['job_id']
            if job_id in jobs:
                data_jobs.append(data)

        return data_jobs


    def free_equipment(experiment_id):
        experiment = Experiment.objects.get(pk=experiment_id)
        experiment.active = False
        experiment.save()

        return experiment

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

    def get_from_rasp_server(url):
        url_to_rest = REST_BASE_URL + url
        response = api_requests.get(url_to_rest)

        return response
