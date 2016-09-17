from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import HttpResponse
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.forms import formset_factory
from datetime import date

from bevim.forms import UserForm, JobForm
from bevim.models import Experiment, Job

class HomeView(View):

    http_method_names = [u'post', u'get']
    template = "home.html"
    form = UserForm
    context = {
        'form' : form,
        'title': "UserForm"
    }
                   
    def get(self, request):
        return render(request, self.template, self.context)

    def post(self, request):

        try:
            form = self.form(data=request.POST)
            if form.is_valid():
                form.save()
                data = form.cleaned_data
                messages.add_message(request, messages.SUCCESS, _('Successfully registered!'))
                response = redirect('/login')
            else:
                self.context['form'] = form
                messages.add_message(request, messages.ERROR, _('Could not perform the registration! Try again.'))
                response = render(request, self.template, self.context) 
        
        except Exception as e:
            response = HttpResponse(str(e))

        return response


class ExperimentView(View):

    http_method_names = [u'post', u'get']
    template = "experiment.html"
    JobFormSet = formset_factory(JobForm)
    formset = JobFormSet
    context = {
        'formset' : formset,
        'title': "ExperimentForm"
    }
                   
    def get(self, request):
        return render(request, self.template, self.context)

    def post(self, request):

        try:
            experiment = self.create_experiment(request.user)
            formset = self.formset(request.POST)
            if formset.is_valid():
                if formset.cleaned_data is not None:
                    for job_data in formset.cleaned_data:
                        self.save_job(job_data, experiment)
                # messages.add_message(request, messages.SUCCESS, _('Successfully registered!'))
                # response = redirect('experiment')
                response = redirect('/login')
            else:
                self.context['formset'] = formset
                # messages.add_message(request, messages.ERROR, _('Could not perform the registration! Try again.'))
                response = render(request, self.template, self.context) 
        
        except Exception as e:
            response = HttpResponse(str(e))

        return response



    def create_experiment(self, user):
        user_experiments = Experiment.objects.filter(user_id=user.pk)
        if user_experiments:
            experiment = Experiment.objects.filter(user_id=user.pk).latest('id')
            last_user_number = experiment.number
            number = last_user_number + 1        
        else:
            number = "{0:0>5}".format(1)
        
        experiment_date = date.today()
        experiment = Experiment(number=number, date=experiment_date, user_id=user.pk)
        experiment.save()

        return experiment

    def save_job(self, job_data, experiment):

        if job_data:
            choose_frequency = job_data['choose_frequency']
            job_time = job_data['job_time']

            job = Job(choose_frequency=choose_frequency, job_time=job_time, experiment_id=experiment.id)
            job.save()
