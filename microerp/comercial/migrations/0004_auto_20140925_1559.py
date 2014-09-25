# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0001_initial'),
        ('comercial', '0003_auto_20140923_1714'),
    ]

    operations = [
        migrations.AddField(
            model_name='followupdepropostacomercial',
            name='visita',
            field=models.BooleanField(default=False, help_text='Indica se houve visita f\xedsica neste FollowUp'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='followupdepropostacomercial',
            name='visita_por',
            field=models.ForeignKey(related_name=b'followup_com_visita_set', blank=True, to='rh.Funcionario', null=True),
            preserve_default=True,
        ),
    ]
