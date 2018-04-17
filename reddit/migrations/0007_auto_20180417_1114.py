# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-04-17 11:14
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('reddit', '0006_auto_20180417_1103'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2018, 4, 17, 11, 14, 51, 924189, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customuser',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]