from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import HttpResponse
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from bevim.forms import UserForm


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

