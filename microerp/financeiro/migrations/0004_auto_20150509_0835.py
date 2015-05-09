# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0003_auto_20150210_1946'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banco',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, blank=True)),
                ('codigo', models.CharField(max_length=100, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='contabancaria',
            name='agencia',
            field=models.CharField(default=1, max_length=100, blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contabancaria',
            name='banco',
            field=models.ForeignKey(default=1, to='financeiro.Banco'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contabancaria',
            name='conta',
            field=models.CharField(default=1, max_length=100, blank=True),
            preserve_default=False,
        ),
    ]
