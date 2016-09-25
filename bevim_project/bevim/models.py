from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator


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
