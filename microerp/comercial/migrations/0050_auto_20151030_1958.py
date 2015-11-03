# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0049_empresacomercial_responsavel_legal'),
    ]

    operations = [
        migrations.AddField(
            model_name='empresacomercial',
            name='responsavel_legal_cpf',
            field=models.CharField(max_length=300, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='empresacomercial',
            name='telefone_celular',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='empresacomercial',
            name='telefone_fixo',
            field=models.CharField(help_text=b'Formato: XX-XXXX-XXXX', max_length=100, null=True, blank=True),
        ),
    ]
