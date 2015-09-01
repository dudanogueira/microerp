# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0008_auto_20150816_0904'),
    ]

    operations = [
        migrations.AddField(
            model_name='precliente',
            name='origem_precliente',
            field=models.ForeignKey(verbose_name=b'Origem do Cliente', blank=True, to='cadastro.ClienteOrigem', null=True),
        ),
    ]
