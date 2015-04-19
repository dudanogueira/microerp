# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0014_auto_20150408_1329'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClasseTipoDeProposta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='tipodeproposta',
            name='classe',
            field=models.ForeignKey(blank=True, to='comercial.ClasseTipoDeProposta', null=True),
            preserve_default=True,
        ),
    ]
