# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-04 04:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tool', '0005_auto_20160701_0735'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='wacc',
            field=models.FloatField(blank=True, null=True, verbose_name='weighted average cost of capital'),
        ),
        migrations.AlterField(
            model_name='stock',
            name='beta',
            field=models.FloatField(blank=True, null=True, verbose_name='beta'),
        ),
    ]