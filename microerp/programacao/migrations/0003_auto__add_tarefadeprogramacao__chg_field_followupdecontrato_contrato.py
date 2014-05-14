# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TarefaDeProgramacao'
        db.create_table(u'programacao_tarefadeprogramacao', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contrato', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['comercial.ContratoFechado'], blank=True)),
            ('cliente', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cadastro.Cliente'])),
            ('status_execucao', self.gf('django.db.models.fields.CharField')(default='naoiniciado', max_length=100)),
            ('porcentagem_execucao', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=3, decimal_places=0)),
            ('aguardando_cliente', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('data_aguardando_cliente', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('data_marcado_emandamento', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('data_marcado_pendente', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('data_marcado_retorno_cliente', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('data_marcado_finalizado', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('data_programada', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('criado_por', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tarefa_de_programacao_adicionado_set', to=orm['rh.Funcionario'])),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'programacao', ['TarefaDeProgramacao'])

        # Adding M2M table for field funcionarios_participantes on 'TarefaDeProgramacao'
        db.create_table(u'programacao_tarefadeprogramacao_funcionarios_participantes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tarefadeprogramacao', models.ForeignKey(orm[u'programacao.tarefadeprogramacao'], null=False)),
            ('funcionario', models.ForeignKey(orm[u'rh.funcionario'], null=False))
        ))
        db.create_unique(u'programacao_tarefadeprogramacao_funcionarios_participantes', ['tarefadeprogramacao_id', 'funcionario_id'])


        # Changing field 'FollowUpDeContrato.contrato'
        db.alter_column(u'programacao_followupdecontrato', 'contrato_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['programacao.TarefaDeProgramacao']))

    def backwards(self, orm):
        # Deleting model 'TarefaDeProgramacao'
        db.delete_table(u'programacao_tarefadeprogramacao')

        # Removing M2M table for field funcionarios_participantes on 'TarefaDeProgramacao'
        db.delete_table('programacao_tarefadeprogramacao_funcionarios_participantes')


        # Changing field 'FollowUpDeContrato.contrato'
        db.alter_column(u'programacao_followupdecontrato', 'contrato_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['comercial.ContratoFechado']))

    models = {
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'cadastro.bairro': {
            'Meta': {'ordering': "['nome']", 'object_name': 'Bairro'},
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
            'designado': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cliente_designado_set'", 'null': 'True', 'to': u"orm['rh.Funcionario']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fantasia': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
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
        u'cadastro.enderecoempresa': {
            'Meta': {'object_name': 'EnderecoEmpresa'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'cnpj_vinculado': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'cadastro.ramo': {
            'Meta': {'object_name': 'Ramo'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'comercial.categoriacontratofechado': {
            'Meta': {'object_name': 'CategoriaContratoFechado'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'comercial.contratofechado': {
            'Meta': {'object_name': 'ContratoFechado'},
            'aguardando_cliente': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'apoio_tecnico': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'contratos_apoio_tecnico'", 'null': 'True', 'to': u"orm['rh.Funcionario']"}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'categoria': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['comercial.CategoriaContratoFechado']", 'null': 'True', 'blank': 'True'}),
            'cliente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cadastro.Cliente']"}),
            'concluido': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data_aguardando_cliente': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'data_marcado_emandamento': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'data_marcado_finalizado': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'data_marcado_pendente': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'data_marcado_retorno_cliente': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'data_validacao': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'documento_proposto_legal': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'efetivo_inicio_execucao': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 4, 8, 0, 0)'}),
            'efetivo_termino_execucao': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'forma_pagamento': ('django.db.models.fields.CharField', [], {'default': "'dinheiro'", 'max_length': '100'}),
            'funcionario_validador': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'contrato_validado_set'", 'null': 'True', 'to': u"orm['rh.Funcionario']"}),
            'funcionarios_participantes': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'contratos_participados'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['rh.Funcionario']"}),
            'garantia': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio_cobranca': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 4, 8, 0, 0)'}),
            'items_incluso': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'items_nao_incluso': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'motivo_invalido': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'nome_proposto_legal': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'numero_termo_de_entrega': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'objeto': ('django.db.models.fields.TextField', [], {}),
            'observacoes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'parcelas': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'porcentagem_execucao': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '3', 'decimal_places': '0'}),
            'previsao_inicio_execucao': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 4, 8, 0, 0)'}),
            'previsao_termino_execucao': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'receber_apos_conclusao': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'responsavel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Funcionario']"}),
            'responsavel_comissionado': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'contrato_comissionado_set'", 'null': 'True', 'to': u"orm['rh.Funcionario']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'emaberto'", 'max_length': '100'}),
            'status_execucao': ('django.db.models.fields.CharField', [], {'default': "'naoiniciado'", 'max_length': '100'}),
            'termo_de_entrega_recebido': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tipo': ('django.db.models.fields.CharField', [], {'default': "'fechado'", 'max_length': '100'}),
            'valor': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'valor_entrada': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'programacao.followupdecontrato': {
            'Meta': {'ordering': "['-criado']", 'object_name': 'FollowUpDeContrato'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'contrato': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['programacao.TarefaDeProgramacao']"}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'criado_por': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'followup_contrato_adicionado_set'", 'to': u"orm['rh.Funcionario']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'porcentagem_execucao': ('django.db.models.fields.DecimalField', [], {'max_digits': '3', 'decimal_places': '0'}),
            'texto': ('django.db.models.fields.TextField', [], {})
        },
        u'programacao.perfilacessoprogramacao': {
            'Meta': {'object_name': 'PerfilAcessoProgramacao'},
            'analista': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'gerente': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'programacao.tarefadeprogramacao': {
            'Meta': {'object_name': 'TarefaDeProgramacao'},
            'aguardando_cliente': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'cliente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cadastro.Cliente']"}),
            'contrato': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['comercial.ContratoFechado']", 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'criado_por': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tarefa_de_programacao_adicionado_set'", 'to': u"orm['rh.Funcionario']"}),
            'data_aguardando_cliente': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'data_marcado_emandamento': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'data_marcado_finalizado': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'data_marcado_pendente': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'data_marcado_retorno_cliente': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'data_programada': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'funcionarios_participantes': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'contratos_participantes_programacao'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['rh.Funcionario']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'porcentagem_execucao': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '3', 'decimal_places': '0'}),
            'status_execucao': ('django.db.models.fields.CharField', [], {'default': "'naoiniciado'", 'max_length': '100'})
        },
        u'rh.cargo': {
            'Meta': {'ordering': "['nome']", 'object_name': 'Cargo'},
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
            'salario_referencia': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'subprocedimentos': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['rh.SubProcedimento']", 'symmetrical': 'False'}),
            'tipo': ('django.db.models.fields.CharField', [], {'default': "'escritorio'", 'max_length': '100', 'blank': 'True'})
        },
        u'rh.competencia': {
            'Meta': {'object_name': 'Competencia'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'grupo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.GrupoDeCompetencia']"}),
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
            'endereco_empresa_designado': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['cadastro.EnderecoEmpresa']"}),
            'escolaridade_conclusao': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 4, 8, 0, 0)', 'null': 'True', 'blank': 'True'}),
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
            'ultima_checagem_endereco': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 4, 8, 0, 0)'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'valor_aluguel': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'valor_hora': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'})
        },
        u'rh.grupodecompetencia': {
            'Meta': {'object_name': 'GrupoDeCompetencia'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'rh.periodotrabalhado': {
            'Meta': {'ordering': "['-criado']", 'object_name': 'PeriodoTrabalhado'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'fim': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Funcionario']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 4, 8, 0, 0)'})
        },
        u'rh.procedimento': {
            'Meta': {'object_name': 'Procedimento'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'codigo': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'departamento': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Departamento']"}),
            'descricao': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'rh.subprocedimento': {
            'Meta': {'object_name': 'SubProcedimento'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'descricao': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'procedimento': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Procedimento']"}),
            'versao': ('django.db.models.fields.IntegerField', [], {'default': '0'})
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

    complete_apps = ['programacao']