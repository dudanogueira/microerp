# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import comercial.models


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0034_auto_20150907_1109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemgrupodocumento',
            name='imagem',
            field=models.ImageField(null=True, upload_to=comercial.models.ImagemDocumentoDir(), blank=True),
        ),
        migrations.AlterField(
            model_name='propostacomercial',
            name='documento_gerado',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='comercial.DocumentoGerado'),
        ),
    ]
