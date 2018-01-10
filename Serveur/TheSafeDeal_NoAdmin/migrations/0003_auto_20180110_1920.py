# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-10 18:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TheSafeDeal_NoAdmin', '0002_auto_20180110_0152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projet',
            name='client',
            field=models.TextField(blank=True, max_length=150),
        ),
        migrations.AlterField(
            model_name='projet',
            name='prestataire',
            field=models.TextField(max_length=150),
        ),
        migrations.AlterField(
            model_name='projet',
            name='prix',
            field=models.DecimalField(decimal_places=2, max_digits=9),
        ),
        migrations.AlterField(
            model_name='projet',
            name='professionnel',
            field=models.TextField(max_length=150),
        ),
        migrations.AlterField(
            model_name='projet',
            name='titre',
            field=models.CharField(max_length=200),
        ),
    ]
