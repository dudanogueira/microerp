# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ControleDeEquipamento'
        db.create_table(u'almoxarifado_controledeequipamento', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('funcionario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Funcionario'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='pendente', max_length=100)),
            ('observacao', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('autorizador', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='autorizacao_controle_equipamento_set', null=True, to=orm['rh.Funcionario'])),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'almoxarifado', ['ControleDeEquipamento'])

        # Adding model 'TipoDeEquipamento'
        db.create_table(u'almoxarifado_tipodeequipamento', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'almoxarifado', ['TipoDeEquipamento'])

        # Adding model 'Produto'
        db.create_table(u'almoxarifado_produto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('medida', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('consumivel', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('estoque_minimo_total', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'almoxarifado', ['Produto'])

        # Adding model 'Equipamento'
        db.create_table(u'almoxarifado_equipamento', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('produto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['almoxarifado.Produto'])),
            ('perdido', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('data_perdido', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('alocado', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('data_de_compra', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 10, 10, 0, 0))),
            ('data_expiracao', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('modelo', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('marca', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('tipo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['almoxarifado.TipoDeEquipamento'])),
            ('quantidade', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'almoxarifado', ['Equipamento'])

        # Adding model 'LinhaControleDeEquipamento'
        db.create_table(u'almoxarifado_linhacontroledeequipamento', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('controle', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['almoxarifado.ControleDeEquipamento'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='pendente', max_length=100)),
            ('devolvido', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('equipamento', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['almoxarifado.Equipamento'])),
            ('receptor', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='receptor_controle_equipamento_set', null=True, to=orm['rh.Funcionario'])),
            ('devolutor', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='devolutor_controle_equipamento_set', null=True, to=orm['rh.Funcionario'])),
            ('data_retirada', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 10, 10, 0, 0))),
            ('quantidade_retirada', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('data_devolucao_programada', self.gf('django.db.models.fields.DateField')()),
            ('data_devolucao_efetiva', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('quantidade_devolvida', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'almoxarifado', ['LinhaControleDeEquipamento'])

        # Adding unique constraint on 'LinhaControleDeEquipamento', fields ['controle', 'equipamento']
        db.create_unique(u'almoxarifado_linhacontroledeequipamento', ['controle_id', 'equipamento_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'LinhaControleDeEquipamento', fields ['controle', 'equipamento']
        db.delete_unique(u'almoxarifado_linhacontroledeequipamento', ['controle_id', 'equipamento_id'])

        # Deleting model 'ControleDeEquipamento'
        db.delete_table(u'almoxarifado_controledeequipamento')

        # Deleting model 'TipoDeEquipamento'
        db.delete_table(u'almoxarifado_tipodeequipamento')

        # Deleting model 'Produto'
        db.delete_table(u'almoxarifado_produto')

        # Deleting model 'Equipamento'
        db.delete_table(u'almoxarifado_equipamento')

        # Deleting model 'LinhaControleDeEquipamento'
        db.delete_table(u'almoxarifado_linhacontroledeequipamento')


    models = {
        u'almoxarifado.controledeequipamento': {
            'Meta': {'object_name': 'ControleDeEquipamento'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'autorizador': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'autorizacao_controle_equipamento_set'", 'null': 'True', 'to': u"orm['rh.Funcionario']"}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Funcionario']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'observacao': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'pendente'", 'max_length': '100'})
        },
        u'almoxarifado.equipamento': {
            'Meta': {'object_name': 'Equipamento'},
            'alocado': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data_de_compra': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 10, 10, 0, 0)'}),
            'data_expiracao': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'data_perdido': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marca': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'modelo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'perdido': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'produto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['almoxarifado.Produto']"}),
            'quantidade': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tipo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['almoxarifado.TipoDeEquipamento']"})
        },
        u'almoxarifado.linhacontroledeequipamento': {
            'Meta': {'unique_together': "(('controle', 'equipamento'),)", 'object_name': 'LinhaControleDeEquipamento'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'controle': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['almoxarifado.ControleDeEquipamento']"}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data_devolucao_efetiva': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'data_devolucao_programada': ('django.db.models.fields.DateField', [], {}),
            'data_retirada': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 10, 10, 0, 0)'}),
            'devolutor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'devolutor_controle_equipamento_set'", 'null': 'True', 'to': u"orm['rh.Funcionario']"}),
            'devolvido': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'equipamento': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['almoxarifado.Equipamento']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quantidade_devolvida': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'quantidade_retirada': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'receptor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'receptor_controle_equipamento_set'", 'null': 'True', 'to': u"orm['rh.Funcionario']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'pendente'", 'max_length': '100'})
        },
        u'almoxarifado.produto': {
            'Meta': {'object_name': 'Produto'},
            'consumivel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'estoque_minimo_total': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medida': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'almoxarifado.tipodeequipamento': {
            'Meta': {'object_name': 'TipoDeEquipamento'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'rh.cargo': {
            'Meta': {'object_name': 'Cargo'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'competencias': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['rh.Competencia']", 'symmetrical': 'False'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
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
        u'rh.competencia': {
            'Meta': {'object_name': 'Competencia'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
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
            'competencias': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['rh.Competencia']", 'null': 'True', 'blank': 'True'}),
            'complemento': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'cpf': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'escolaridade_conclusao': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 10, 10, 0, 0)', 'null': 'True', 'blank': 'True'}),
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
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
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
            'inicio': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 10, 10, 0, 0)'})
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

    complete_apps = ['almoxarifado']