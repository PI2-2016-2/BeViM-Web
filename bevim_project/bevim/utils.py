from django.db import connection, IntegrityError, transaction
import json
import requests as api_requests

from bevim.models import Experiment, Job, Sensor, Acceleration, Amplitude, Frequency, Speed
from bevim_project.settings import REST_BASE_URL
from django.db.models.signals import post_save
from django.core.serializers.json import DjangoJSONEncoder


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

    def save_data(experiment_data, data_class):
        #experiment_data = ExperimentUtils.get_data_by_jobs(jobs, data_type)
        # if experiment_data:
        first_job = None
        with transaction.atomic():
            for data in experiment_data:
                if len(data) == 6: # Just for simulation - DROP THIS
                    sensor = Sensor.objects.get(name=data[0])
                    job = Job.objects.get(pk=data[5])
                    first_job = job
                    data_class.objects.create(sensor=sensor, x_value=data[1], y_value=data[2],
                                            z_value=data[3], timestamp=data[4], job=job)

        if first_job is not None:
            experiment = first_job.experiment
            return experiment

        return None

    def get_data_by_jobs(jobs, data_type):
        response = RestUtils.get_from_rasp_server('v1/' + data_type)
        experiment_data = json.loads(response.content.decode('utf8'))

        data_jobs = {}
        if experiment_data:
          for data in experiment_data:
            job_id = data['job_id']
            data_jobs[job_id] = []
            if job_id in jobs:
                data_jobs[job_id].append(data)

        return data_jobs


    def free_equipment(experiment_id):
        experiment = Experiment.objects.get(pk=experiment_id)
        experiment.active = False
        experiment.save()

        return experiment

    def get_experiment_result(experiment_id, only_acceleration=False):
        jobs = Job.objects.filter(experiment=experiment_id)

        accelerations = []
        amplitudes = []
        frequencies = []
        speeds = []
    
        for job in jobs:
            job_accelerations = job.acceleration_set.all()
            if job_accelerations:
                accelerations.append(job_accelerations)

                if not only_acceleration:
                    job_amplitudes = job.amplitude_set.all()
                    amplitudes.append(job_amplitudes)
                    job_frequencies = job.frequency_set.all()
                    frequencies.append(job_frequencies)
                    job_speeds = job.speed_set.all()
                    speeds.append(job_speeds)

        result = {
            'accelerations' : accelerations, 
            'amplitudes': amplitudes, 
            'frequencies': frequencies, 
            'speeds': speeds
        }
        return result

    def get_chart_data(result_data):
        timestamps = ['x']
        data_values = ['data']
        for job_data in result_data:
            for data in job_data:
                timestamps.append(data.timestamp)
                data_values.append(data.x_value)

        columns = [timestamps, data_values]
        chart_data = {
            'x' : 'x',
            'columns': columns,
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
