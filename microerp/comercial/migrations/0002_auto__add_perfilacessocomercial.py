# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PerfilAcessoComercial'
        db.create_table(u'comercial_perfilacessocomercial', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('gerente', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('analista', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['account.User'], unique=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'comercial', ['PerfilAcessoComercial'])


    def backwards(self, orm):
        # Deleting model 'PerfilAcessoComercial'
        db.delete_table(u'comercial_perfilacessocomercial')


    models = {
        u'account.user': {
            'Meta': {'object_name': 'User'},
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'})
        },
        u'cadastro.bairro': {
            'Meta': {'object_name': 'Bairro'},
            'cidade': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cadastro.Cidade']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'cadastro.cidade': {
            'Meta': {'object_name': 'Cidade'},
            'estado': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'cadastro.cliente': {
            'Meta': {'object_name': 'Cliente'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'cnpj': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'contato': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'cpf': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fantasia': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'funcionario_responsavel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Funcionario']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_referencia': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'inscricao_estadual': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'nascimento': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'observacao': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'origem': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cadastro.ClienteOrigem']", 'null': 'True', 'blank': 'True'}),
            'ramo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cadastro.Ramo']", 'null': 'True', 'blank': 'True'}),
            'rg': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'solicitar_consulta_credito': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'telefone_celular': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'telefone_fixo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'})
        },
        u'cadastro.clienteorigem': {
            'Meta': {'object_name': 'ClienteOrigem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'observacao': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'cadastro.ramo': {
            'Meta': {'object_name': 'Ramo'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'comercial.contatocomercial': {
            'Meta': {'object_name': 'ContatoComercial'},
            'agenda_fonte': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['comercial.FonteDeAgendaComercial']", 'null': 'True', 'blank': 'True'}),
            'cliente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cadastro.Cliente']", 'null': 'True', 'blank': 'True'}),
            'fim': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Funcionario']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_referencia': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'inicio': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'o_dia_todo': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'observacao': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'solicitacao_comercial_convertida': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['comercial.SolicitacaoComercial']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'programado'", 'max_length': '100'}),
            'ultima_alteracao': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'comercial.fontedeagendacomercial': {
            'Meta': {'object_name': 'FonteDeAgendaComercial'},
            'descricao': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Funcionario']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tipo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['comercial.TipoContatoComercial']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'comercial.perfilacessocomercial': {
            'Meta': {'object_name': 'PerfilAcessoComercial'},
            'analista': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'gerente': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['account.User']", 'unique': 'True'})
        },
        u'comercial.solicitacaocomercial': {
            'Meta': {'object_name': 'SolicitacaoComercial'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'cliente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cadastro.Cliente']"}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data_convertido': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'data_finalizado': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'follow_up': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'observacao': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'aberta'", 'max_length': '100'}),
            'tipo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['comercial.TipoSolicitacaoComercial']"}),
            'valor': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'comercial.tipocontatocomercial': {
            'Meta': {'object_name': 'TipoContatoComercial'},
            'cor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'cor_do_texto': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'comercial.tiposolicitacaocomercial': {
            'Meta': {'object_name': 'TipoSolicitacaoComercial'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mao_de_obra_inclusa': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'permite_valor_variavel': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'valor': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'rh.cargo': {
            'Meta': {'object_name': 'Cargo'},
            'departamento': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Departamento']"}),
            'descricao': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dias_renovacao_exames': ('django.db.models.fields.IntegerField', [], {'default': '365'}),
            'exame_medico_padrao': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['rh.TipoDeExameMedico']", 'symmetrical': 'False'}),
            'gratificacao': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'periculosidade': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'salario_referencia': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        },
        u'rh.departamento': {
            'Meta': {'object_name': 'Departamento'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'rh.funcionario': {
            'Meta': {'ordering': "['nome']", 'object_name': 'Funcionario'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'bairro': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cadastro.Bairro']"}),
            'cargo_atual': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'funcionario_cargo_atual_set'", 'null': 'True', 'to': u"orm['rh.Cargo']"}),
            'cargo_inicial': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'funcionario_cargo_inicial_set'", 'to': u"orm['rh.Cargo']"}),
            'carteira_habilitacao_categoria': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'carteira_habilitacao_expedicao': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'carteira_habilitacao_numero': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'carteira_habilitacao_vencimento': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'carteira_profissional_emissao': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'carteira_profissional_numero': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'carteira_profissional_serie': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'cep': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'certificado_reservista': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'complemento': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'cpf': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'escolaridade_conclusao': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 4, 30, 0, 0)', 'null': 'True', 'blank': 'True'}),
            'escolaridade_cursos': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'escolaridade_nivel': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'escolaridade_serie_inconclusa': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'estado_civil': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'forma_de_pagamento': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'foto': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'funcionario_superior': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Funcionario']", 'null': 'True', 'blank': 'True'}),
            'gratificacao': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_de_trabalho': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'membro_cipa': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'nacionalidade': ('django.db.models.fields.CharField', [], {'default': "'Brasil'", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'nascimento': ('django.db.models.fields.DateField', [], {}),
            'naturalidade': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'nome_companheiro': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'nome_mae': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'nome_pai': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'numero': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'numero_lre': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'observacao': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'periodo_trabalhado_corrente': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'periodo_trabalhado_corrente'", 'unique': 'True', 'null': 'True', 'to': u"orm['rh.PeriodoTrabalhado']"}),
            'pis': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'residencia': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rg': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rg_data': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'rg_expeditor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rua': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'salario_atual': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'salario_inicial': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'sexo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'telefone_celular': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'telefone_fixo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'telefone_recado': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'titulo_eleitor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['account.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'valor_aluguel': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'valor_hora': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'})
        },
        u'rh.periodotrabalhado': {
            'Meta': {'ordering': "['-criado']", 'object_name': 'PeriodoTrabalhado'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'fim': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Funcionario']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 4, 30, 0, 0)'})
        },
        u'rh.tipodeexamemedico': {
            'Meta': {'object_name': 'TipoDeExameMedico'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'descricao': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'valor': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        }
    }

    complete_apps = ['comercial']