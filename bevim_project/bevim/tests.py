from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.core.serializers.json import DjangoJSONEncoder

from .forms import JobFormSet
from .models import Sensor, Job, Experiment, Acceleration
from .utils import ExperimentUtils

from unittest.mock import patch
import json

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
        
        self.experiment = Experiment.objects.create(id=1, number=1, user=self.user, active=True)
        self.job = Job.objects.create(choose_frequency=20, job_time=10, experiment=self.experiment)
        sensor = Sensor.objects.create(id=1, name='1')
        self.acceleration = Acceleration.objects.create(sensor=sensor, x_value='2.0', y_value='2.0', z_value='3.0', 
                                    timestamp='0.0', job=self.job)

        
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

    def test_if_get_job_times(self):
        job_2 = Job.objects.create(choose_frequency=20, job_time=30, experiment=self.experiment)
        self.login()
        url_to_test = reverse('timer', kwargs={'experiment_id': self.experiment.id})
        response = self.client.get(url_to_test)
        expected = "\"total_time\": 40"
        self.assertIn(expected, response.context['jobs_info'])

    def test_experiment_result(self):
        url_to_test = reverse('experiment_result', kwargs={'experiment_id': self.experiment.id})
        response = self.client.get(url_to_test)
        expected_x_axis = "\"x\", \"0.00\""
        expected_y_axis = "x Tempo\", \"2.00\""
        self.assertIn(expected_x_axis, response.context['accelerations_chart_data'])
        self.assertIn(expected_y_axis, response.context['accelerations_chart_data'])

    def test_process_result_with_not_processed_data(self):
        url_to_test = reverse('process_result', kwargs={'experiment_id': self.experiment.id})
        response_post = self.client.post(url_to_test)
        # If the data was not processed yet the responde is the 'process_result' url 
        self.assertContains(response_post, url_to_test)

    def test_process_result_with_processed_data(self):
        url_to_test = reverse('process_result', kwargs={'experiment_id': self.experiment.id})

        self.experiment.active = False
        self.experiment.save()
        response_post = self.client.post(url_to_test)
        # If the data was not processed yet the responde is the 'experiment_result' url 
        expected_url = reverse('experiment_result', kwargs={'experiment_id': self.experiment.id})
        self.assertContains(response_post, expected_url)

    def test_show_experiments(self):
        url_to_test = reverse('experiments')
        self.login()
        response = self.client.get(url_to_test)    

        self.assertContains(response, '0001') # Experiment number

class TestUtils(TestCase):

    def setUp(self):
        self.username = "maria"
        self.password = "maria"
        self.user = User.objects.create_user(username=self.username, password=self.password)

        self.experiment = Experiment.objects.create(id=1, number=1, user=self.user, active=True)
        self.job = Job.objects.create(id=1, choose_frequency=20, job_time=10, experiment=self.experiment)
        sensor = Sensor.objects.create(id=1, name='1')

    def test_if_free_equipment(self):
        ExperimentUtils.free_equipment(self.experiment.id)

        experiment_after_free = Experiment.objects.get(pk=self.experiment.id)
        self.assertFalse(experiment_after_free.active)

    def test_save_data_with_accelerations(self):
        data = [[1, '2.0', '2.0', '2.0', '0.0', 1]]
        ExperimentUtils.save_data(data, Acceleration)

        accelerations = Acceleration.objects.all()
        self.assertEqual(str(accelerations[0].x_value), '2.00')

    def test_process_data(self):
        data = [[1, 2.0, 2.0, 2.0, 0.0, 1]]
        processed_data = ExperimentUtils.process_data(data)
        
        expected_processed_data = [[1, 0.0, 0.0, 0.0, 0.0, 1]]
        self.assertEqual(processed_data, expected_processed_data)