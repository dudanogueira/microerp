# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bairro',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, verbose_name=b'Nome do Bairro')),
            ],
            options={
                'ordering': ['nome'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cidade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, verbose_name=b'Nome da Cidade')),
                ('estado', models.CharField(max_length=2, choices=[('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amap\xe1'), ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Cear\xe1'), ('DF', 'Distrito Federal'), ('ES', 'Esp\xedrito Santo'), ('GO', 'Goi\xe1s'), ('MA', 'Maranh\xe3o'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'), ('PA', 'Par\xe1'), ('PB', 'Para\xedba'), ('PR', 'Paran\xe1'), ('PE', 'Pernambuco'), ('PI', 'Piau\xed'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'), ('RO', 'Rond\xf4nia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'), ('SP', 'S\xe3o Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', django_extensions.db.fields.UUIDField(max_length=36, editable=False, blank=True)),
                ('id_referencia', models.IntegerField(null=True, blank=True)),
                ('nome', models.CharField(max_length=300, verbose_name='Nome do Cliente')),
                ('fantasia', models.CharField(max_length=500, null=True, verbose_name='Nome de Fantasia', blank=True)),
                ('tipo', models.CharField(max_length=10, verbose_name='Tipo de Cliente', choices=[(b'pf', 'Pessoa F\xedsica'), (b'pj', 'Pessoa Jur\xeddica')])),
                ('cnpj', models.CharField(max_length=255, null=True, verbose_name='CNPJ', blank=True)),
                ('inscricao_estadual', models.CharField(max_length=100, null=True, blank=True)),
                ('cpf', models.CharField(max_length=255, null=True, verbose_name='CPF', blank=True)),
                ('rg', models.CharField(max_length=100, null=True, blank=True)),
                ('nascimento', models.DateField(null=True, verbose_name='Data de Nascimento/Cria\xe7\xe3o', blank=True)),
                ('observacao', models.TextField(null=True, verbose_name='Observa\xe7\xf5es Gerais', blank=True)),
                ('contato', models.CharField(max_length=300, verbose_name=b'Nome do Contato', blank=True)),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
                ('telefone_fixo', models.CharField(help_text=b'Formato: XX-XXXX-XXXX', max_length=100, null=True, blank=True)),
                ('telefone_celular', models.CharField(max_length=100, null=True, blank=True)),
                ('fax', models.CharField(max_length=100, blank=True)),
                ('solicitar_consulta_credito', models.BooleanField(default=False, help_text=b'Marque esta op\xc3\xa7\xc3\xa3o para solicitar uma consulta de cr\xc3\xa9dito', verbose_name=b'Solicitar Consulta de Cr\xc3\xa9dito')),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClienteOrigem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100)),
                ('observacao', models.TextField(null=True, verbose_name='Observa\xe7\xf5es Gerais', blank=True)),
            ],
            options={
                'verbose_name': 'Origem do Cliente',
                'verbose_name_plural': 'Origens dos Clientes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConsultaDeCredito',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('realizada', models.BooleanField(default=False)),
                ('data_solicitacao', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Data de Solicita\xc3\xa7\xc3\xa3o')),
                ('data_realizacao', models.DateTimeField(null=True, verbose_name=b'Data de Realiza\xc3\xa7\xc3\xa3o', blank=True)),
                ('regular', models.BooleanField(default=True, verbose_name=b'Situa\xc3\xa7\xc3\xa3o Regular')),
                ('requisicao', models.CharField(max_length=400, verbose_name=b'Requisi\xc3\xa7\xc3\xa3o')),
                ('observacoes', models.TextField(null=True, verbose_name='Observa\xe7\xf5es', blank=True)),
                ('dados_originais', models.TextField(help_text=b'Este campo deve ser usado para armazenar o retorno de um webservice em seu formato original', null=True, verbose_name=b'Dados Originais', blank=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
            ],
            options={
                'verbose_name': 'Consulta de Cr\xe9dito',
                'verbose_name_plural': 'Consultas de Cr\xe9dito',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EnderecoCliente',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('principal', models.NullBooleanField(default=None, help_text=b'Endere\xc3\xa7o Principal')),
                ('telefone', models.CharField(help_text=b'Formato: XX-XXXX-XXXX', max_length=100, null=True, verbose_name=b'Telefone Associado', blank=True)),
                ('cep', models.CharField(max_length=100, verbose_name='CEP', blank=True)),
                ('rua', models.CharField(max_length=500, verbose_name='Rua', blank=True)),
                ('numero', models.CharField(max_length=100, verbose_name='N\xfamero', blank=True)),
                ('complemento', models.CharField(max_length=200, verbose_name='Complemento', blank=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
            ],
            options={
                'ordering': ('-principal',),
                'verbose_name': 'Endere\xe7o de Cliente',
                'verbose_name_plural': 'Endere\xe7os de Clientes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EnderecoEmpresa',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cnpj_vinculado', models.CharField(max_length=100, blank=True)),
                ('nome', models.CharField(max_length=100)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PerfilAcessoRecepcao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gerente', models.BooleanField(default=False)),
                ('analista', models.BooleanField(default=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
            ],
            options={
                'verbose_name': 'Perfil de Acesso \xe0 Recep\xe7\xe3o',
                'verbose_name_plural': 'Perfis de Acesso \xe0 Recep\xe7\xe3o',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PerfilClienteLogin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PreCliente',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=300)),
                ('contato', models.CharField(max_length=100)),
                ('dados', models.TextField(blank=True)),
                ('sem_interesse', models.BooleanField(default=False)),
                ('sem_interesse_motivo', models.TextField(verbose_name=b'Motivo do Desinteresse', blank=True)),
                ('sem_interesse_data', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('data_convertido', models.DateField(null=True, blank=True)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
            ],
            options={
                'verbose_name': 'Pr\xe9 Cliente',
                'verbose_name_plural': 'Pr\xe9 Clientes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PreClienteSemInteresseOpcao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ramo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100)),
                ('tipo', models.CharField(max_length=10, verbose_name='Tipo de Cliente', choices=[(b'pf', 'Pessoa F\xedsica'), (b'pj', 'Pessoa Jur\xeddica')])),
            ],
            options={
                'verbose_name': 'Ramo de Atua\xe7\xe3o',
                'verbose_name_plural': 'Ramos de Atua\xe7\xe3o',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Recado',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('texto', models.TextField(verbose_name=b'Texto do Recado')),
                ('tipo', models.CharField(default=b'comercial', max_length=100, verbose_name=b'Tipo de Recado', choices=[(b'compra', b'Solicita\xc3\xa7\xc3\xa3o de Compra'), (b'ocorrencia', b'Registro de Ocorr\xc3\xaancia'), (b'comercial', b'Solicita\xc3\xa7\xc3\xa3o Comercial'), (b'informacao_geral', 'Solicita\xe7\xe3o de Informa\xe7\xe3o'), (b'ofertar_produto', 'Oferta de Produto'), (b'agendamento_reuniao', 'Agendamento de Reuni\xe3o'), (b'informacao_projeto', 'Informa\xe7\xe3o sobre Projeto')])),
                ('tipo_outros', models.TextField(blank=True)),
                ('lido', models.BooleanField(default=False)),
                ('lido_em', models.DateTimeField(null=True, blank=True)),
                ('email_enviado', models.BooleanField(default=False)),
                ('encaminhado', models.BooleanField(default=False)),
                ('encaminhado_data', models.DateTimeField(default=datetime.datetime.now)),
                ('criado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Criado', auto_now_add=True)),
                ('atualizado', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'Atualizado', auto_now=True)),
            ],
            options={
                'ordering': ['-criado'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TipoDeConsultaDeCredito',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, blank=True)),
                ('codigo', models.CharField(help_text=b'C\xc3\xb3digo de Identifica\xc3\xa7\xc3\xa3o: cpf, cnpj, cheque, etc', max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
