# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-26 00:14
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bevim', '0003_auto_20160925_1737'),
    ]

    operations = [
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x_value', models.DecimalField(decimal_places=2, max_digits=4)),
                ('y_value', models.DecimalField(decimal_places=2, max_digits=4)),
                ('z_value', models.DecimalField(decimal_places=2, max_digits=4)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=3, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9_\\s+]+$', 'Use alphanumeric characters and underscore only')], verbose_name='Sensor name')),
            ],
        ),
        migrations.CreateModel(
            name='Acceleration',
            fields=[
                ('data_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bevim.Data')),
            ],
            bases=('bevim.data',),
        ),
        migrations.CreateModel(
            name='Amplitude',
            fields=[
                ('data_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bevim.Data')),
            ],
            bases=('bevim.data',),
        ),
        migrations.CreateModel(
            name='Frequency',
            fields=[
                ('data_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bevim.Data')),
            ],
            bases=('bevim.data',),
        ),
        migrations.CreateModel(
            name='Speed',
            fields=[
                ('data_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='bevim.Data')),
            ],
            bases=('bevim.data',),
        ),
        migrations.AddField(
            model_name='data',
            name='sensor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bevim.Sensor', verbose_name='Sensor'),
        ),
    ]
