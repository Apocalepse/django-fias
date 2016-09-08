# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-25 04:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fias', '0009_add_fks_to_normdoc'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('roomguid', models.UUIDField(primary_key=True, serialize=False)),
                ('roomid', models.UUIDField(db_index=True, unique=True)),
                ('previd', models.UUIDField(blank=True, null=True)),
                ('nextid', models.UUIDField(blank=True, null=True)),
                ('flatnumber', models.CharField(max_length=50)),
                ('flattype', models.IntegerField()),
                ('roomnumber', models.CharField(blank=True, max_length=50, null=True)),
                ('roomtype', models.IntegerField(blank=True, null=True)),
                ('regioncode', models.CharField(max_length=2)),
                ('postalcode', models.PositiveIntegerField(blank=True, null=True)),
                ('updatedate', models.DateField()),
                ('startdate', models.DateField()),
                ('enddate', models.DateField()),
                ('livestatus', models.BooleanField(default=False)),
                ('normdoc', models.UUIDField(blank=True, null=True)),
                ('cadnum', models.CharField(blank=True, max_length=100, null=True)),
                ('roomcadnum', models.CharField(blank=True, max_length=100, null=True)),
                ('houseguid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fias.House')),
                ('operstatus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fias.OperStat')),
            ],
            options={
                'verbose_name_plural': 'Помещения',
                'verbose_name': 'Помещение',
            },
        ),
        migrations.CreateModel(
            name='Stead',
            fields=[
                ('ifnsfl', models.PositiveIntegerField(blank=True, null=True)),
                ('terrifnsfl', models.PositiveIntegerField(blank=True, null=True)),
                ('ifnsul', models.PositiveIntegerField(blank=True, null=True)),
                ('terrifnsul', models.PositiveIntegerField(blank=True, null=True)),
                ('okato', models.BigIntegerField(blank=True, null=True)),
                ('oktmo', models.BigIntegerField(blank=True, null=True)),
                ('postalcode', models.PositiveIntegerField(blank=True, null=True)),
                ('updatedate', models.DateField()),
                ('startdate', models.DateField()),
                ('enddate', models.DateField()),
                ('normdoc', models.UUIDField(blank=True, null=True)),
                ('cadnum', models.CharField(blank=True, max_length=100, null=True)),
                ('divtype', models.CharField(default=0, max_length=1)),
                ('steadguid', models.UUIDField(primary_key=True, serialize=False)),
                ('parentguid', models.UUIDField(blank=True, db_index=True, null=True)),
                ('steadid', models.UUIDField(unique=True)),
                ('previd', models.UUIDField(blank=True, null=True)),
                ('nextid', models.UUIDField(blank=True, null=True)),
                ('number', models.CharField(blank=True, max_length=120, null=True)),
                ('regioncode', models.CharField(max_length=2)),
                ('livestatus', models.BooleanField(default=False)),
                ('operstatus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fias.OperStat')),
            ],
            options={
                'verbose_name_plural': 'Земельные участки',
                'verbose_name': 'Земельный участок',
            },
        ),
    ]