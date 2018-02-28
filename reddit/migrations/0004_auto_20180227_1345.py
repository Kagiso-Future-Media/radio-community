# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-02-27 13:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0003_auto_20180223_1254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/radio_com/%Y/%m/%d/'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/radio_com/%Y/%m/%d/'),
        ),
    ]
