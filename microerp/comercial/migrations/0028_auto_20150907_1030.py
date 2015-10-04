# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0027_auto_20150907_1026'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orcamento',
            name='documento_gerado',
        ),
        migrations.AddField(
            model_name='propostacomercial',
            name='documento_gerado',
            field=models.OneToOneField(null=True, blank=True, to='comercial.DocumentoGerado'),
        ),
    ]
