# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-09-17 14:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bevim', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='experiment',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='job',
            old_name='experiment_id',
            new_name='experiment',
        ),
    ]
