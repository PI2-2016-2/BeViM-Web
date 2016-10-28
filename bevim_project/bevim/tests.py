from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from unittest.mock import patch
from .forms import JobFormSet
from .models import Sensor, Job, Experiment


class TestViews(TestCase):

    def setUp(self):
        self.username = "maria"
        self.password = "maria"
        self.user = User.objects.create_user(username=self.username, password=self.password)

        self.experiment_data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '',
            'form-0-choose_frequency': '50',
            'form-0-job_time': '10',
            'form-1-choose_frequency': '100',
            'form-1-job_time': '20',
        }
        
    def login(self):
        self.client.login(username=self.username, password=self.password)
        

    def test_start_experiment_post(self):
        url_to_test = reverse('new_experiment')
        self.login()

        response = self.client.post(url_to_test, self.experiment_data, follow=True)
        self.assertContains(response, _("Experiment time"))

    def test_start_experiment_with_frequency_greater_than_100(self):
        url_to_test = reverse('new_experiment')
        self.login()

        data = self.experiment_data 
        data['form-0-choose_frequency'] = '101'
        response = self.client.post(url_to_test, data, follow=True)

        self.assertContains(response, _('Certifique-se que este valor seja menor ou igual a 100.'))


    def test_start_experiment_with_frequency_less_than_0(self):
        url_to_test = reverse('new_experiment')
        self.login()

        data = self.experiment_data 
        data['form-0-choose_frequency'] = '-1'
        response = self.client.post(url_to_test, data, follow=True)

        self.assertContains(response, _('Certifique-se que este valor seja maior ou igual a 0.'))


    def test_if_job_was_saved(self):
        url_to_test = reverse('new_experiment')
        self.login()

        self.client.post(url_to_test, self.experiment_data, follow=True)

        job = Job.objects.get(choose_frequency='50')
        self.assertTrue(job.job_time, '10')

    @patch('bevim.views.ExperimentView.get_sensors',
           return_value=[Sensor(name="S1"), Sensor(name="S2")])
    def test_if_detect_busy_equipment(self, sensors):

        self.login()
        url_to_test = reverse('new_experiment')
        response_1 = self.client.post(url_to_test, self.experiment_data, follow=True)

        another_user = User.objects.create_user(username="joao", password="joao")
        self.client.login(username="joao", password="joao") # Login with another user
        response_2 = self.client.get(url_to_test)
        
        self.assertContains(response_2, _('The equipment is in use by another user.'))

    @patch('bevim.views.ExperimentView.get_sensors',
           return_value=[Sensor(name="S1"), Sensor(name="S2")])
    def test_if_get_sensors(self, sensors):
        url_to_test = reverse('new_experiment')
        self.login()

        response = self.client.get(url_to_test)
        self.assertTemplateUsed(response, "new_experiment.html")
        self.assertContains(response, "S1")

    def test_if_free_equipment(self):
        
        experiment = Experiment.objects.create(id=1, number=1, user=self.user, active=True)
        from .utils import ExperimentUtils
        ExperimentUtils.free_equipment(experiment.id)

        experiment_after_free = Experiment.objects.get(pk=experiment.id)
        self.assertFalse(experiment_after_free.active)

