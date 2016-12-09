from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from itertools import chain


class Experiment(models.Model):
    number = models.PositiveSmallIntegerField()
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField()
    initial_time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return str(self.number)

    @staticmethod
    def parse_data_to_show(experiments):

        experiments_with_correct_data = []
        for experiment in experiments:
            number = experiment.number
            experiment.number = "{0:0>5}".format(number)
            date = experiment.date
            experiment.date = date.strftime("%d/%m/%y")
            experiments_with_correct_data.append(experiment)

        return experiments_with_correct_data

    @staticmethod
    def get_active_sensors_by_experiment(experiment_id):
        experiment = Experiment.objects.get(pk=experiment_id)
        jobs = experiment.job_set.all()
        jobs_sensors = []
        if jobs:
            for job in jobs:
                job_sensors = job.acceleration_set.all().values('sensor_id').distinct()
                jobs_sensors = list(chain(jobs_sensors, job_sensors))

        experiment_sensors = []
        if jobs_sensors:
            for job_sensor in jobs_sensors:
                job_sensor_id = job_sensor['sensor_id']
                sensor = Sensor.objects.get(pk=job_sensor_id)
                if not sensor in experiment_sensors:
                    experiment_sensors.append(sensor)

        return experiment_sensors

class Job(models.Model):
    choose_frequency = models.PositiveSmallIntegerField(_('Frequency'),
        validators=[MaxValueValidator(100)])
    job_time = models.PositiveSmallIntegerField(_('Time in seconds'))
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.pk)

class Sensor(models.Model):
    name = models.CharField(
        "Sensor name",
        max_length=3,
        validators=[
            validators.RegexValidator(
                r'^[a-zA-Z0-9_\s+]+$',
                'Use alphanumeric characters and underscore only'
            )
        ],
        blank=False,
        unique=True
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ExperimentFrequency(models.Model):
    experiment = models.ForeignKey(Experiment, verbose_name='Experiment')
    frequency = models.IntegerField()
    timestamp = models.IntegerField()


class Data(models.Model):
    sensor = models.ForeignKey(Sensor, verbose_name='Sensor')
    x_value = models.DecimalField(max_digits=30, decimal_places=2)
    y_value = models.DecimalField(max_digits=30, decimal_places=2)
    z_value = models.DecimalField(max_digits=30, decimal_places=2)
    timestamp = models.DecimalField(max_digits=17, decimal_places=2)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Acceleration(Data):
    pass


class Speed(Data):
    pass


class Amplitude(Data):
    pass


class Frequency(Data):
    pass
