# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cadastro', '0006_auto_20150125_2034'),
    ]

    operations = [
        migrations.AddField(
            model_name='enderecocliente',
            name='bairro_texto',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='enderecocliente',
            name='cidade_texto',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='enderecocliente',
            name='uf_texto',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='consultadecredito',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='consultadecredito',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='enderecocliente',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='enderecocliente',
            name='bairro',
            field=models.ForeignKey(blank=True, to='cadastro.Bairro', null=True),
        ),
        migrations.AlterField(
            model_name='enderecocliente',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='enderecoempresa',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='enderecoempresa',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='perfilacessorecepcao',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='perfilacessorecepcao',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='perfilclientelogin',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='perfilclientelogin',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
        migrations.AlterField(
            model_name='precliente',
            name='atualizado',
            field=models.DateTimeField(auto_now=True, verbose_name=b'Atualizado'),
        ),
        migrations.AlterField(
            model_name='precliente',
            name='criado',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Criado'),
        ),
    ]
