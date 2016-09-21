from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator


class Experiment(models.Model):
    number = models.PositiveSmallIntegerField()
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

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
    choose_frequency = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(100)])
    job_time = models.PositiveSmallIntegerField()
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.pk)
