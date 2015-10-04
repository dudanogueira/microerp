# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0045_itemgrupodocumento_imagem_editavel'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemgrupodocumento',
            name='titulo_exibir',
            field=models.CharField(help_text='Caso n\xe3o exista um T\xedtulo para impress\xe3o, usar este', max_length=150, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='itemgrupodocumento',
            name='titulo',
            field=models.CharField(help_text='T\xedtulo para Impress\xe3o', max_length=150, null=True, blank=True),
        ),
    ]
