# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cadastro', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recado',
            name='adicionado_por',
            field=models.ForeignKey(related_name=b'recado_criado_set', to='rh.Funcionario'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recado',
            name='cliente',
            field=models.ForeignKey(verbose_name=b'Cliente Associado (opcional)', blank=True, to='cadastro.Cliente', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recado',
            name='destinatario',
            field=models.ForeignKey(related_name=b'recado_recebido_set', to='rh.Funcionario'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recado',
            name='remetente',
            field=models.ForeignKey(related_name=b'recado_enviado_set', to='rh.Funcionario'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='precliente',
            name='adicionado_por',
            field=models.ForeignKey(related_name=b'precliente_lancado_set', to='rh.Funcionario'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='precliente',
            name='cliente_convertido',
            field=models.OneToOneField(null=True, blank=True, to='cadastro.Cliente'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='precliente',
            name='convertido_por',
            field=models.ForeignKey(related_name=b'precliente_convertido_set', blank=True, to='rh.Funcionario', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='precliente',
            name='designado',
            field=models.ForeignKey(related_name=b'precliente_designado_set', verbose_name=b'Funcion\xc3\xa1rio Designado', blank=True, to='rh.Funcionario', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='precliente',
            name='sem_interesse_opcao',
            field=models.ForeignKey(verbose_name=b'Op\xc3\xa7\xc3\xa3o de Desinteresse', blank=True, to='cadastro.PreClienteSemInteresseOpcao', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='perfilclientelogin',
            name='cliente',
            field=models.OneToOneField(null=True, blank=True, to='cadastro.Cliente', verbose_name=b'Cliente Cadastrado no Sistema'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='perfilclientelogin',
            name='user',
            field=models.OneToOneField(null=True, blank=True, to=settings.AUTH_USER_MODEL, verbose_name=b'Usu\xc3\xa1rio do Sistema'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='perfilacessorecepcao',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='enderecocliente',
            name='bairro',
            field=models.ForeignKey(to='cadastro.Bairro'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='enderecocliente',
            name='cliente',
            field=models.ForeignKey(to='cadastro.Cliente'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='enderecocliente',
            unique_together=set([('principal', 'cliente')]),
        ),
        migrations.AddField(
            model_name='consultadecredito',
            name='cliente',
            field=models.ForeignKey(to='cadastro.Cliente'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='consultadecredito',
            name='funcionario_executor',
            field=models.ForeignKey(related_name=b'realizacoes_consulta_credito_set', to='rh.Funcionario'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='consultadecredito',
            name='funcionario_solicitante',
            field=models.ForeignKey(related_name=b'solicitacoes_consulta_credito_set', to='rh.Funcionario'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='consultadecredito',
            name='tipo',
            field=models.ForeignKey(verbose_name=b'Tipo da Consulta', to='cadastro.TipoDeConsultaDeCredito'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cliente',
            name='designado',
            field=models.ForeignKey(related_name=b'cliente_designado_set', verbose_name=b'Funcion\xc3\xa1rio Designado', blank=True, to='rh.Funcionario', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cliente',
            name='origem',
            field=models.ForeignKey(verbose_name=b'Origem do Cliente', blank=True, to='cadastro.ClienteOrigem', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cliente',
            name='ramo',
            field=models.ForeignKey(blank=True, to='cadastro.Ramo', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bairro',
            name='cidade',
            field=models.ForeignKey(to='cadastro.Cidade'),
            preserve_default=True,
        ),
    ]
