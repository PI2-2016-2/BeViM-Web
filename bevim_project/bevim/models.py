from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.core import validators


class Experiment(models.Model):
    number = models.PositiveSmallIntegerField()
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField()
    initial_time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return str(self.number)


class Job(models.Model):
    choose_frequency = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(100)])
    job_time = models.PositiveSmallIntegerField()
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
        blank=False
    )

    def __str__(self):
        return self.name


class Data(models.Model):
    sensor = models.ForeignKey(Sensor, verbose_name='Sensor')
    x_value = models.DecimalField(max_digits=4, decimal_places=2)
    y_value = models.DecimalField(max_digits=4, decimal_places=2)
    z_value = models.DecimalField(max_digits=4, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)


class Acceleration(Data):
    pass


class Speed(Data):
    pass


class Amplitude(Data):
    pass


class Frequency(Data):
    pass
