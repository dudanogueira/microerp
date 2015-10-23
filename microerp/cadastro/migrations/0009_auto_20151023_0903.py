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
            name='bairro_texto',
            field=models.CharField(max_length=100, null=True, verbose_name=b'Bairro', blank=True),
        ),
        migrations.AddField(
            model_name='precliente',
            name='cep',
            field=models.CharField(max_length=100, verbose_name='CEP', blank=True),
        ),
        migrations.AddField(
            model_name='precliente',
            name='cidade_texto',
            field=models.CharField(max_length=100, null=True, verbose_name=b'Cidade', blank=True),
        ),
        migrations.AddField(
            model_name='precliente',
            name='complemento',
            field=models.CharField(max_length=200, verbose_name='Complemento', blank=True),
        ),
        migrations.AddField(
            model_name='precliente',
            name='numero',
            field=models.CharField(max_length=100, verbose_name='N\xfamero', blank=True),
        ),
        migrations.AddField(
            model_name='precliente',
            name='rua',
            field=models.CharField(max_length=500, verbose_name='Rua', blank=True),
        ),
        migrations.AddField(
            model_name='precliente',
            name='telefone_celular',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='precliente',
            name='telefone_fixo',
            field=models.CharField(help_text=b'Formato: XX-XXXX-XXXX', max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='precliente',
            name='uf_texto',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name=b'Estado', choices=[('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amap\xe1'), ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Cear\xe1'), ('DF', 'Distrito Federal'), ('ES', 'Esp\xedrito Santo'), ('GO', 'Goi\xe1s'), ('MA', 'Maranh\xe3o'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'), ('PA', 'Par\xe1'), ('PB', 'Para\xedba'), ('PR', 'Paran\xe1'), ('PE', 'Pernambuco'), ('PI', 'Piau\xed'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'), ('RO', 'Rond\xf4nia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'), ('SP', 'S\xe3o Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')]),
        ),
    ]
