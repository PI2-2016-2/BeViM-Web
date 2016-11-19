from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.core import validators
from django.utils.translation import ugettext_lazy as _


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


class Data(models.Model):
    sensor = models.ForeignKey(Sensor, verbose_name='Sensor')
    x_value = models.DecimalField(max_digits=10, decimal_places=2)
    y_value = models.DecimalField(max_digits=10, decimal_places=2)
    z_value = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DecimalField(max_digits=17, decimal_places=2 )
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
