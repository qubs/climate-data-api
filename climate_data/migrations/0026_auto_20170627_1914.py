# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-27 19:14
from __future__ import unicode_literals

import django.contrib.postgres.fields.ranges
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('climate_data', '0025_auto_20170627_1850'),
    ]

    operations = [
        migrations.AddField(
            model_name='datatype',
            name='bounds_2',
            field=django.contrib.postgres.fields.ranges.FloatRangeField(default='[-2147483648,2147483647)'),
        ),
        migrations.AlterField(
            model_name='datatype',
            name='bounds',
            field=django.contrib.postgres.fields.ranges.IntegerRangeField(default='[-2147483648,2147483647]'),
        ),
    ]
