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
from django.core import serializers
from django.core.urlresolvers import reverse

from datetime import date
import json
import requests

from bevim.forms import UserForm, JobForm
from bevim.models import Experiment, Job, Sensor, Acceleration
from bevim import tasks
from bevim.utils import ExperimentUtils, RestUtils
from bevim import protocol


def change_frequency(request):
    new_frequency = request.POST['frequency']
    job = request.POST['job']
    jobs_info = request.POST['jobs_info']
    payload = {'frequency': new_frequency, 'job': job, 'jobs_info': jobs_info}
    response = RestUtils.post_to_rasp_server('v1/control/change_frequency', payload)
    return HttpResponse(response.status_code)

def consult_frequency(request):
    response = RestUtils.get_from_rasp_server('v1/consult/current_frequency')
    return HttpResponse(response.content)

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
        active_experiment = Experiment.objects.filter(active=True)
        if active_experiment:
            busy_equipment = True
            messages.add_message(
                request,
                messages.ERROR,
                _('The equipment is in use by another user.'))
        else:
            busy_equipment = False
        self.context['formset'] = self.JobFormSet
        self.context['busy_equipment'] = busy_equipment
        self.context['sensors'] = self.get_sensors()
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
                    'job_pk': job.pk,
                    'frequency': job.choose_frequency,
                    'time': job.job_time
                }
                total_time += job.job_time
                i += 1

            dict_jobs = {
                'jobs': jobs_info,
                'total_time': total_time
            }

            json_jobs = json.dumps(dict_jobs)

        context = {
            'jobs_info' : json_jobs,
            'experiment_id': experiment_id,
        }

        return render(request, "timer.html", context)

    def stop_experiment(self, request, experiment_id):
        if experiment_id:
            experiment = ExperimentUtils.free_equipment(experiment_id)

            # Sending signal to stop experiment on the control system
            payload = {'flag': protocol.STOP_EXPERIMENT_FLAG}
            RestUtils.put_to_rasp_server('v1/control/change_frequency', payload)
            response = HttpResponse(reverse('process_result', kwargs={'experiment_id':experiment_id}))
        else:
            response = HttpResponseBadRequest()

        return response

    @csrf_exempt
    def experiment_result(self, request=None, experiment_id=None):
        accelerations = ExperimentUtils.get_experiment_accelerations(experiment_id)
        context = {
            'accelerations': accelerations,
            'experiment_id': experiment_id,
        }
        
        return render(request, "result.html", context)

    @csrf_exempt
    def process_result(self, request, experiment_id):
        if request.method == 'GET':
            template = "stop_experiment_modal.html"
            response = render(request, template, {'experiment_id': experiment_id})

        elif request.method == 'POST':
            accelerations = ExperimentUtils.get_experiment_accelerations(experiment_id)
            if accelerations:
                url_name = 'experiment_result'
            else:   
                url_name = 'process_result'

            response = HttpResponse(reverse(url_name, kwargs={'experiment_id':experiment_id}))

        return response

    @csrf_exempt
    def receive_result(self, request):
        response = HttpResponseBadRequest()
        if request.body:
            accelerations = json.loads(request.body.decode('utf8'))
            experiment = ExperimentUtils.save_data(accelerations, Acceleration)
            if experiment is not None:
                response =  HttpResponse(experiment.id)

        return response

    def get_sensors(self, request=None):
        response = None
        try:
            payload = {'value': protocol.GET_AVAILABLE_SENSORS_FLAG}
            response = RestUtils.post_to_rasp_server('v1/sensor', payload)
        except (requests.exceptions.Timeout,
                requests.exceptions.ConnectionError):

            if request is not None:
                # sensors = False -> Means that there is no connection to the server
                html = render_to_string(u'found_sensors_list.html', {'sensors': False})
                response = HttpResponse(html)
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
                response = HttpResponse(html)
            else:
                response = sensors
        finally:
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
