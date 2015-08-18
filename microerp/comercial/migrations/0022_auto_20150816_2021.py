# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comercial', '0021_auto_20150815_1717'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmpresaComercial',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=300)),
                ('nome_reduzido', models.CharField(max_length=300)),
                ('principal', models.BooleanField()),
                ('cnpj', models.CharField(max_length=300)),
                ('logradouro', models.CharField(max_length=300)),
                ('numero', models.IntegerField()),
                ('complemento', models.CharField(max_length=300, null=True, blank=True)),
                ('cep', models.CharField(max_length=300)),
                ('bairro', models.CharField(max_length=300)),
                ('cidade', models.CharField(max_length=300)),
                ('estado', models.CharField(blank=True, max_length=100, null=True, verbose_name=b'Estado', choices=[('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amap\xe1'), ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Cear\xe1'), ('DF', 'Distrito Federal'), ('ES', 'Esp\xedrito Santo'), ('GO', 'Goi\xe1s'), ('MA', 'Maranh\xe3o'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'), ('PA', 'Par\xe1'), ('PB', 'Para\xedba'), ('PR', 'Paran\xe1'), ('PE', 'Pernambuco'), ('PI', 'Piau\xed'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'), ('RO', 'Rond\xf4nia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'), ('SP', 'S\xe3o Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')])),
            ],
        ),
        migrations.AddField(
            model_name='perfilacessocomercial',
            name='empresa',
            field=models.ForeignKey(blank=True, to='comercial.EmpresaComercial', null=True),
        ),
    ]
