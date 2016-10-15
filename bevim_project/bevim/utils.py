from django.db import connection, IntegrityError
import json
import requests as api_requests

from bevim.models import Experiment, Job, Sensor, Acceleration
from bevim_project.settings import REST_BASE_URL


# Util methods - Controller

class ExperimentUtils:

    def populate_database(experiment):
        jobs = experiment.job_set.all()
        if jobs:
            jobs_ids = []
            for job in jobs:
                jobs_ids.append(job.id)

            if jobs_ids:
                ExperimentUtils.save_data(jobs_ids, "acceleration")
                ExperimentUtils.save_data(jobs_ids, "amplitude")
                ExperimentUtils.save_data(jobs_ids, "frequency")
                ExperimentUtils.save_data(jobs_ids, "speed")

    def save_data(jobs, data_type):
       
        experiment_data = ExperimentUtils.get_data_by_jobs(jobs, data_type)
        values = ExperimentUtils.get_values_to_insert(experiment_data)
        
        if values != "":
            try:
                # Start transaction
                DatabaseUtils.execute_query("START TRANSACTION;")
            
                # Inserting on mother table (Data)
                values = values[0:(len(values) - 1)]
                first_id = DatabaseUtils.insert_experiment_data(values)
                
                # Inserting ids on child table (Acceleration)
                DatabaseUtils.insert_child_ids(data_type, first_id[0], len(experiment_data))

                # Commit transaction
                DatabaseUtils.execute_query("COMMIT;")

            except IntegrityError:
                # Commit transaction
                DatabaseUtils.execute_query("ROLLBACK;")

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

    def get_values_to_insert(experiment_data):
        values = ""
        if experiment_data:
            for data in experiment_data:
                sensor_data = data['sensor']
                sensor = Sensor.objects.get(name=sensor_data['name'])
                job = Job.objects.get(pk=data['job_id'])
                values += "('"+ str(sensor.id) + "', '"+ data['x_value'] + "', '"+ data['y_value'] + "', '"+ data['z_value'] + "', '"+ data['timestamp'] + "', '"+ str(job.id) + "'),"

        return values

    def free_equipment(experiment_id):
        experiment = Experiment.objects.get(pk=experiment_id)
        experiment.active = False
        experiment.save()

        return experiment

class RestUtils:
    
    def post_to_rasp_server(url, data, headers=None):
        url_to_rest = REST_BASE_URL + url
        if headers is None:
            headers = {'content-type': 'application/json'}
        response = api_requests.post(url_to_rest, data=json.dumps(data),
                        headers=headers)
        return response

    def get_from_rasp_server(url):
        url_to_rest = REST_BASE_URL + url
        response = api_requests.get(url_to_rest)

        return response


class DatabaseUtils:

    def execute_query(query):
        with connection.cursor() as cursor:
            try:
                cursor.execute(query)
                row = cursor.fetchone()
            except:
                raise IntegrityError

        return row

    def insert_experiment_data(values):
        try:
            query = "INSERT INTO `bevim_data` (`sensor_id`, `x_value`, `y_value`, `z_value`, `timestamp`, `job_id`) VALUES " + values
            DatabaseUtils.execute_query(query);

            query_to_get_id = "SELECT last_insert_id();"
            last_id = DatabaseUtils.execute_query(query_to_get_id);    
            
            return last_id
        
        except IntegrityError:
            raise IntegrityError

    def insert_child_ids(table, first_id, number_of_accelerations):

        values = ""
        limit = first_id + number_of_accelerations
        for data_id in range(first_id, limit):
            values += "(" + str(data_id) + ")," 

        try:
            query = "INSERT INTO `bevim_" + table +"` (`data_ptr_id`) VALUES " + values[0:(len(values) - 1)]
            DatabaseUtils.execute_query(query);

        except IntegrityError:
            raise IntegrityError