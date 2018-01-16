# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-16 10:44
from __future__ import unicode_literals

import TheSafeDeal_NoAdmin.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TheSafeDeal_NoAdmin', '0006_auto_20180115_2037'),
    ]

    operations = [
        migrations.AddField(
            model_name='files',
            name='projet_key',
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AlterField(
            model_name='files',
            name='document',
            field=models.FileField(upload_to=TheSafeDeal_NoAdmin.models.directory_path),
        ),
    ]