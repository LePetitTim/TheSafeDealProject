# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-10 22:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TheSafeDeal_NoAdmin', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='projet',
            field=models.CharField(blank=True, max_length=32),
        ),
    ]
