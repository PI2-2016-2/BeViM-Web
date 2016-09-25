# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-09-25 17:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bevim', '0002_auto_20160917_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='active',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='experiment',
            name='initial_time',
            field=models.TimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='experiment',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
