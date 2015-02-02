# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('solicitacao', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CanalSolicitacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='solicitacao',
            name='canal',
            field=models.ForeignKey(verbose_name=b'Canal da Solicita\xc3\xa7\xc3\xa3o', blank=True, to='solicitacao.CanalSolicitacao', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='solicitacao',
            name='prazo',
            field=models.DateField(default=datetime.datetime(2015, 2, 5, 19, 38, 14, 54548)),
        ),
        migrations.AlterField(
            model_name='solicitacao',
            name='tipo',
            field=models.ForeignKey(verbose_name=b'Tipo de Solicita\xc3\xa7\xc3\xa3o', blank=True, to='solicitacao.TipoSolicitacao', null=True),
        ),
    ]
