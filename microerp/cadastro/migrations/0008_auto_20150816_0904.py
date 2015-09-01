# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0007_auto_20150815_1717'),
    ]

    operations = [
        migrations.AddField(
            model_name='precliente',
            name='cnpj',
            field=models.CharField(max_length=255, null=True, verbose_name='CNPJ', blank=True),
        ),
        migrations.AddField(
            model_name='precliente',
            name='cpf',
            field=models.CharField(max_length=255, null=True, verbose_name='CPF', blank=True),
        ),
        migrations.AddField(
            model_name='precliente',
            name='numero_instalacao',
            field=models.CharField(max_length=300, null=True, verbose_name='N\xfamero da Instala\xe7\xe3o', blank=True),
        ),
        migrations.AddField(
            model_name='precliente',
            name='origem',
            field=models.ForeignKey(verbose_name=b'Origem do Cliente', blank=True, to='cadastro.ClienteOrigem', null=True),
        ),
        migrations.AddField(
            model_name='precliente',
            name='tipo',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Tipo de Pr\xe9 Cliente', choices=[(b'pf', 'Pessoa F\xedsica'), (b'pj', 'Pessoa Jur\xeddica')]),
        ),
        migrations.AlterField(
            model_name='enderecocliente',
            name='bairro_texto',
            field=models.CharField(max_length=100, null=True, verbose_name=b'Bairro', blank=True),
        ),
        migrations.AlterField(
            model_name='enderecocliente',
            name='cidade_texto',
            field=models.CharField(max_length=100, null=True, verbose_name=b'Cidade', blank=True),
        ),
        migrations.AlterField(
            model_name='enderecocliente',
            name='uf_texto',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name=b'Estado', choices=[('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amap\xe1'), ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Cear\xe1'), ('DF', 'Distrito Federal'), ('ES', 'Esp\xedrito Santo'), ('GO', 'Goi\xe1s'), ('MA', 'Maranh\xe3o'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'), ('PA', 'Par\xe1'), ('PB', 'Para\xedba'), ('PR', 'Paran\xe1'), ('PE', 'Pernambuco'), ('PI', 'Piau\xed'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'), ('RO', 'Rond\xf4nia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'), ('SP', 'S\xe3o Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')]),
        ),
    ]
