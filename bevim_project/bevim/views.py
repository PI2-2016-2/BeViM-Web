from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.forms import formset_factory
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse

from datetime import date
import json
import requests

from bevim.forms import UserForm, JobForm
from bevim.models import Experiment, Job, Sensor, Acceleration, Speed, Amplitude
from bevim.utils import ExperimentUtils, RestUtils
from bevim import protocol


def change_frequency(request):
    new_frequency = request.POST['frequency']
    job = request.POST['job']
    jobs_info = request.POST['jobs_info']
    experiment = request.POST['experiment']
    payload = {
        'experiment': experiment,
        'frequency': new_frequency,
        'job': job,
        'jobs_info': jobs_info
    }
    response = RestUtils.post_to_rasp_server('v1/control/change_frequency', payload)
    return HttpResponse(response.status_code)

def consult_frequency(request):
    response = RestUtils.get_from_rasp_server('v1/consult/current_frequency')
    return HttpResponse(response.content)

def about(request):
    return render(request, "about.html", {})

def how_to_use(request):
    return render(request, "how_to_use.html", {})

class HomeView(View):

    http_method_names = [u'post', u'get']
    template = "home.html"
    form = UserForm
    context = {
        'form': form,
        'title': "UserForm"
    }

    def get(self, request):
        return render(request, self.template, self.context)

    def post(self, request):

        try:
            form = self.form(data=request.POST)
            if form.is_valid():
                form.save()
                messages.add_message(
                    request,
                    messages.SUCCESS, _('Successfully registered!'))

                response = redirect('/login')
            else:
                self.context['form'] = form
                messages.add_message(
                    request,
                    messages.ERROR,
                    _('Could not perform the registration! Try again.'))

                response = render(request, self.template, self.context)

        except Exception as e:
            response = HttpResponse(str(e))

        return response


class ExperimentView(View):

    accelerations = []

    http_method_names = [u'post', u'get']
    template = "new_experiment.html"
    JobFormSet = formset_factory(JobForm)
    formset = JobFormSet
    context = {
        'title': "ExperimentForm"
    }

    @method_decorator(login_required)
    def get(self, request):
        # Checking if has a user using the equipment
        # active_experiment = Experiment.objects.filter(active=True)
        # if active_experiment:
        #     busy_equipment = True
        #     messages.add_message(
        #         request,
        #         messages.ERROR,
        #         _('The equipment is in use by another user.'))
        # else:
        #     busy_equipment = False
        available_sensors = self.get_sensors()
        self.context['formset'] = self.JobFormSet
        # self.context['busy_equipment'] = busy_equipment
        self.context['busy_equipment'] = False
        self.context['sensors'] = available_sensors
        self.context['sensors_active'] = available_sensors is not None
        return render(request, self.template, self.context)

    @method_decorator(login_required)
    def post(self, request):
        try:
            formset = self.formset(request.POST)
            if formset.is_valid():
                response = self.get_data_from_jobs(formset, request)
            else:
                self.context['formset'] = formset
                response = render(request, self.template, self.context)

        except Exception as e:
            response = HttpResponse(str(e))

        return response

    @method_decorator(login_required)
    def show_timer(self, request, experiment_id=None):
        if experiment_id is not None:
            experiment = Experiment.objects.get(pk=experiment_id)
            jobs = experiment.job_set.all()

            total_time = 0
            jobs_info = {}
            i = 1
            for job in jobs:
                jobs_info[i] = {
                    'order': i,
                    'job_pk': job.pk,
                    'frequency': job.choose_frequency,
                    'time': job.job_time
                }
                total_time += job.job_time
                i += 1

            dict_jobs = {
                'experiment_id': experiment_id,
                'jobs': jobs_info,
                'total_time': total_time
            }

            json_jobs = json.dumps(dict_jobs)

        context = {
            'jobs_info' : json_jobs,
            'experiment_id': experiment_id,
        }

        # Inform to the server that a new experiment is going to start
        try:
            RestUtils.get_from_rasp_server(
                'v1/control/change_frequency',
                {'experiment': experiment_id}
            )
        except requests.exceptions.ConnectionError as e:
            print(e)

        return render(request, "timer.html", context)

    def stop_experiment(self, request, experiment_id):
        if experiment_id:
            # Sending signal to stop experiment on the control system
            payload = {'experiment': experiment_id, 'forced_stop': request.POST['forcedStop']}
            RestUtils.put_to_rasp_server('v1/control/change_frequency', payload)
            response = HttpResponse(reverse('process_result', kwargs={'experiment_id':experiment_id}))
        else:
            response = HttpResponseBadRequest()

        return response

    @csrf_exempt
    def experiment_result(self, request=None, experiment_id=None):
        # Show charts of the first active sensor
        active_sensors = Experiment.get_active_sensors_by_experiment(experiment_id)
        sensor_id = active_sensors[0].id
        experiment_result = ExperimentUtils.get_experiment_result(experiment_id, sensor_id)
        response = self.render_experiment_result(request, experiment_result, experiment_id, sensor_id)

        return response

    @csrf_exempt
    def experiment_result_by_sensor(self, request=None, experiment_id=None, sensor_id=None):
        experiment_result = ExperimentUtils.get_experiment_result(experiment_id, sensor_id)
        response = self.render_experiment_result(request, experiment_result, experiment_id, sensor_id)

        return response

    def render_experiment_result(self, request, experiment_result, experiment_id, active_sensor):
        initial_timestamp = json.dumps(experiment_result['jobs_initial_timestamp'])
        active_sensors = Experiment.get_active_sensors_by_experiment(experiment_id)

        frequency_chart_data = ExperimentUtils.get_frequency_charts(experiment_id)
        context = {
            'accelerations_chart_data': experiment_result['accelerations_chart_data'],
            'amplitudes_chart_data': experiment_result['amplitudes_chart_data'],
            # 'frequencies_chart_data': experiment_result['frequencies_chart_data'],
            'frequencies_chart_data': frequency_chart_data,
            'speeds_chart_data': experiment_result['speeds_chart_data'],
            'experiment_id': experiment_id,
            'initial_timestamp': initial_timestamp,
            'jobs_quantity': len(experiment_result['jobs_initial_timestamp']),
            'active_sensors': active_sensors,
            'active_sensor': active_sensor
        }

        return render(request, "result.html", context)


    @csrf_exempt
    def process_result(self, request, experiment_id):
        experiment = Experiment.objects.get(pk=experiment_id)
        if request.method == 'GET':
            jobs = experiment.job_set.all()
            total_time = 0
            for job in jobs:
                total_time += job.job_time

            template = "stop_experiment.html"
            response = render(request, template, {'experiment_id': experiment_id, 'total_time': total_time})

        elif request.method == 'POST':
            if experiment.active:
                url_name = 'process_result'
            else:
                url_name = 'experiment_result'


            response = HttpResponse(reverse(url_name, kwargs={'experiment_id':experiment_id}))

        return response

    @csrf_exempt
    def receive_result(self, request):
        response = HttpResponseBadRequest()
        if request.body:
            # Get data
            data = json.loads(request.body.decode('utf8'))

            accelerations = data['sensors']
            experiment = ExperimentUtils.save_data(accelerations, Acceleration)

            ExperimentUtils.save_frequency(data['frequencies'], experiment)

            speeds = ExperimentUtils.process_data(accelerations)
            ExperimentUtils.save_data(speeds, Speed)

            amplitudes = ExperimentUtils.process_data(speeds)
            ExperimentUtils.save_data(amplitudes, Amplitude)

            # End experiment
            ExperimentUtils.free_equipment(experiment.id)
            if experiment is not None:
                response =  HttpResponse(experiment.id)

        return response

    def get_sensors(self, request=None):
        response = None
        try:
            response = RestUtils.post_to_rasp_server('v1/sensor')
        except (requests.exceptions.Timeout,
                requests.exceptions.ConnectionError):

            if request is not None:
                # sensors = False -> Means that there is no connection to the server
                html = render_to_string(u'found_sensors_list.html', {'sensors': False})
                response = JsonResponse({'active': False, 'html': html})
            else:
                response = None
        else:
            sensors = None
            if response.content:
                received_sensors = json.loads(response.content.decode('utf8'))

                if received_sensors:
                    sensors = []
                    for received_sensor in received_sensors:
                        sensor = Sensor.objects.update_or_create(name=received_sensor['name'], active=True)
                        sensors.append(sensor[0])

            if request is not None:
                html = render_to_string(u'found_sensors_list.html', {'sensors': sensors})
                response = JsonResponse({'active': True, 'html': html})
            else:
                response = sensors
        finally:
            return response

    def show_experiments(self, request):
        user = request.user
        experiments = user.experiment_set.all()
        experiments = Experiment.parse_data_to_show(experiments)
        template = "experiments.html"
        context = {
            'experiments': experiments
        }
        response = render(request, template, context)

        return response

    def create_experiment(self, user):
        user_experiments = Experiment.objects.filter(user_id=user.pk)
        if user_experiments:
            experiment = Experiment.objects.filter(
                user_id=user.pk).latest('id')
            number = experiment.number + 1
        else:
            number = "{0:0>5}".format(1)

        experiment = Experiment(number=number,
                                user_id=user.pk,
                                active = True)
        experiment.save()

        return experiment

    def get_data_from_jobs(self, formset, request):
        empty_job = 0
        try:
            with transaction.atomic():

                experiment = self.create_experiment(request.user)
                if formset.cleaned_data is not None:
                    for job_data in formset.cleaned_data:
                        if job_data:
                            self.save_job(job_data, experiment)
                        else:
                            empty_job += 1

                if empty_job != len(formset.cleaned_data):
                    response = redirect('timer', experiment_id=experiment.id)

                else:
                    raise IntegrityError

        except IntegrityError:
            self.context['formset'] = formset
            messages.add_message(
                request,
                messages.ERROR,
                _('It is not possible start '
                    'an experiment without one frequency '
                    'and one time. Please fill the fields.'))

            response = render(request, self.template, self.context)

        return response

    def save_job(self, job_data, experiment):
        if job_data:
            choose_frequency = job_data['choose_frequency']
            job_time = job_data['job_time']

            job = Job(
                choose_frequency=choose_frequency,
                job_time=job_time,
                experiment_id=experiment.id)
            job.save()
