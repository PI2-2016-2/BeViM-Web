from scipy import integrate

from django.db import connection, IntegrityError, transaction
import json
import requests as api_requests
from itertools import chain

from bevim.models import Experiment, Job, Sensor, Acceleration, Amplitude, Frequency, Speed
from bevim_project.settings import REST_BASE_URL
from django.db.models.signals import post_save
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import ugettext as _


# Util methods - Controller

class ExperimentUtils:

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


    def get_experiment_result(experiment_id, sensor_id):
        jobs = Job.objects.filter(experiment=experiment_id)

        accelerations = []
        amplitudes = []
        frequencies = []
        speeds = []
        jobs_initial_timestamp = []

        for job in jobs:
            job_accelerations = job.acceleration_set.all()
            if job_accelerations:
                job_amplitudes = job.amplitude_set.all()
                job_frequencies = job.frequency_set.all()
                job_speeds = job.speed_set.all()

                sensor_accelerations = job_accelerations.filter(sensor_id=sensor_id) 
                sensor_amplitudes = job_amplitudes.filter(sensor_id=sensor_id)
                sensor_frequencies = job_frequencies.filter(sensor_id=sensor_id)
                sensor_speeds = job_speeds.filter(sensor_id=sensor_id)

                if sensor_accelerations:
                    jobs_initial_timestamp.append(str(sensor_accelerations[0].timestamp))
                    accelerations = list(chain(accelerations, sensor_accelerations))
                    amplitudes = list(chain(amplitudes, sensor_amplitudes))
                    frequencies = list(chain(frequencies, sensor_frequencies))
                    speeds = list(chain(speeds, sensor_speeds))

        frequencies_chart_data = ExperimentUtils.get_chart_data(frequencies, _('Frequency x Time'), '#0080ff')
        accelerations_chart_data = ExperimentUtils.get_chart_data(accelerations, _('Acceleration x Time'), '#b30000')
        amplitudes_chart_data = ExperimentUtils.get_chart_data(amplitudes, _('Amplitude x Time'), '#ff8000')
        speeds_chart_data = ExperimentUtils.get_chart_data(speeds, _('Speed x Time'), '#8000ff')


        result = {
            'accelerations_chart_data' : accelerations_chart_data,
            'amplitudes_chart_data': amplitudes_chart_data,
            'frequencies_chart_data': frequencies_chart_data,
            'speeds_chart_data': speeds_chart_data,
            'jobs_initial_timestamp': jobs_initial_timestamp
        }
        return result

    def get_chart_data(result_data, chart_description, color):
        timestamps = ['x']
        data_values = [chart_description]
        if result_data:
            for data in result_data:
                timestamps.append(data.timestamp)
                # data_values.append(data.x_value) # Get sensor data from axis z
                data_values.append(data.z_value) # Get sensor data from axis z

            columns = [timestamps, data_values]
            chart_data = {
                'x' : 'x',
                'columns': columns,
                'colors': {chart_description: color}
                # 'type': 'spline'
            }
        else:
            chart_data = {}

        chart_data = json.dumps(chart_data, cls=DjangoJSONEncoder)
        return chart_data

    def process_data(data_array):
        timestamps = []
        x_values = []
        y_values = []
        z_values = []

        for data in data_array:
            timestamps.append(data[4])
            x_values.append(int(data[1]))
            y_values.append(int(data[2]))
            z_values.append(int(data[3]))

        data_processed_x_axis = integrate.cumtrapz(x_values, timestamps, initial=0)
        data_processed_y_axis = integrate.cumtrapz(y_values, timestamps, initial=0)
        data_processed_z_axis = integrate.cumtrapz(z_values, timestamps, initial=0)
        data_processed = ExperimentUtils.format_integral_array(data_processed_x_axis, data_processed_y_axis, data_processed_z_axis, data_array[:])

        return data_processed

    def format_integral_array(data_processed_x_axis, data_processed_y_axis, data_processed_z_axis, data_array):
        i = 0

        data_processed = data_array[:]
        for data in data_processed:
            data[1] = data_processed_x_axis[i]
            data[2] = data_processed_y_axis[i]
            data[3] = data_processed_z_axis[i]
            i += 1

        return data_processed

class RestUtils:

    TIMEOUT = 10 # In seconds

    @classmethod
    def post_to_rasp_server(cls, url, data=None, headers=None):
        url_to_rest = REST_BASE_URL + url
        if headers is None:
            headers = {'content-type': 'application/json'}
        response = api_requests.post(url_to_rest, data=json.dumps(data),
                        headers=headers, timeout=cls.TIMEOUT)
        return response

    @classmethod
    def put_to_rasp_server(cls, url, data=None, headers=None):
        url_to_rest = REST_BASE_URL + url
        if headers is None:
            headers = {'content-type': 'application/json'}
        response = api_requests.put(url_to_rest, data=json.dumps(data),
                        headers=headers, timeout=cls.TIMEOUT)
        return response

    @classmethod
    def get_from_rasp_server(cls, url, params=None):
        url_to_rest = REST_BASE_URL + url
        response = api_requests.get(url_to_rest, params=params, timeout=cls.TIMEOUT)
        return response
