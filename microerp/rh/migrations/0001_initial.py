# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Funcionario'
        db.create_table('rh_funcionario', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=36, blank=True)),
            ('foto', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, null=True, blank=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('nascimento', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 11, 4, 0, 0))),
            ('observacao', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('telefone_fixo', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('telefone_celular', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('cidade', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cadastro.Cidade'])),
            ('bairro', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cadastro.Bairro'])),
            ('cep', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('rua', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('numero', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('complemento', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('salario_inicial', self.gf('django.db.models.fields.FloatField')()),
            ('cargo_inicial', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cargo_inicial', to=orm['rh.Cargo'])),
            ('cargo_atual', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cargo_atual', to=orm['rh.Cargo'])),
            ('departamento', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Departamento'])),
            ('funcionario_superior', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Funcionario'], null=True, blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal('rh', ['Funcionario'])

        # Adding model 'Cargo'
        db.create_table('rh_cargo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('salario_referencia', self.gf('django.db.models.fields.FloatField')(blank=True)),
        ))
        db.send_create_signal('rh', ['Cargo'])

        # Adding model 'Departamento'
        db.create_table('rh_departamento', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('grupo_responsavel', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='grupo_responsavel', null=True, to=orm['auth.Group'])),
            ('grupo_analista', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='grupo_analista', null=True, to=orm['auth.Group'])),
        ))
        db.send_create_signal('rh', ['Departamento'])

        # Adding model 'PeriodoTrabalhado'
        db.create_table('rh_periodotrabalhado', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('funcionario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Funcionario'])),
            ('inicio', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 11, 4, 0, 0))),
            ('fim', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal('rh', ['PeriodoTrabalhado'])

        # Adding model 'PromocaoSalario'
        db.create_table('rh_promocaosalario', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('aprovado', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('avaliado', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('descricao', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('data_solicitacao', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 11, 4, 0, 0))),
            ('data_resolucao', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('beneficiario', self.gf('django.db.models.fields.related.ForeignKey')(related_name='beneficiario', to=orm['rh.Funcionario'])),
            ('solicitante', self.gf('django.db.models.fields.related.ForeignKey')(related_name='solicitante', to=orm['rh.Funcionario'])),
            ('autorizador', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='autorizador', null=True, to=orm['rh.Funcionario'])),
            ('valor', self.gf('django.db.models.fields.FloatField')()),
            ('periodo_trabalhado', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.PeriodoTrabalhado'])),
            ('observacao', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal('rh', ['PromocaoSalario'])

        # Adding model 'PromocaoCargo'
        db.create_table('rh_promocaocargo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('funcionario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Funcionario'])),
            ('cargo_antigo', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cargo_antigo', to=orm['rh.Cargo'])),
            ('cargo_novo', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cargo_novo', to=orm['rh.Cargo'])),
            ('periodo_trabalhado', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.PeriodoTrabalhado'])),
            ('data', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 11, 4, 0, 0))),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal('rh', ['PromocaoCargo'])

        # Adding model 'SolicitacaoDeLicenca'
        db.create_table('rh_solicitacaodelicenca', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('funcionario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Funcionario'])),
            ('inicio', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 11, 4, 0, 0))),
            ('fim', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 11, 4, 0, 0))),
            ('status', self.gf('django.db.models.fields.CharField')(default='aberta', max_length=100)),
            ('tipo', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('data_criado', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 11, 4, 0, 0))),
            ('data_autorizado', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('processado_por', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='autorizado_por', null=True, to=orm['rh.Funcionario'])),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal('rh', ['SolicitacaoDeLicenca'])


    def backwards(self, orm):
        # Deleting model 'Funcionario'
        db.delete_table('rh_funcionario')

        # Deleting model 'Cargo'
        db.delete_table('rh_cargo')

        # Deleting model 'Departamento'
        db.delete_table('rh_departamento')

        # Deleting model 'PeriodoTrabalhado'
        db.delete_table('rh_periodotrabalhado')

        # Deleting model 'PromocaoSalario'
        db.delete_table('rh_promocaosalario')

        # Deleting model 'PromocaoCargo'
        db.delete_table('rh_promocaocargo')

        # Deleting model 'SolicitacaoDeLicenca'
        db.delete_table('rh_solicitacaodelicenca')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'cadastro.bairro': {
            'Meta': {'object_name': 'Bairro'},
            'cidade': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cadastro.Cidade']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'cadastro.cidade': {
            'Meta': {'object_name': 'Cidade'},
            'estado': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'rh.cargo': {
            'Meta': {'object_name': 'Cargo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'salario_referencia': ('django.db.models.fields.FloatField', [], {'blank': 'True'})
        },
        'rh.departamento': {
            'Meta': {'object_name': 'Departamento'},
            'grupo_analista': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'grupo_analista'", 'null': 'True', 'to': "orm['auth.Group']"}),
            'grupo_responsavel': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'grupo_responsavel'", 'null': 'True', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'rh.funcionario': {
            'Meta': {'ordering': "['nome']", 'object_name': 'Funcionario'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'bairro': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cadastro.Bairro']"}),
            'cargo_atual': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cargo_atual'", 'to': "orm['rh.Cargo']"}),
            'cargo_inicial': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cargo_inicial'", 'to': "orm['rh.Cargo']"}),
            'cep': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'cidade': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cadastro.Cidade']"}),
            'complemento': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'departamento': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.Departamento']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'foto': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'funcionario_superior': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.Funcionario']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nascimento': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 11, 4, 0, 0)'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'numero': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'observacao': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'rua': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'salario_inicial': ('django.db.models.fields.FloatField', [], {}),
            'telefone_celular': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'telefone_fixo': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'})
        },
        'rh.periodotrabalhado': {
            'Meta': {'object_name': 'PeriodoTrabalhado'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'fim': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.Funcionario']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 11, 4, 0, 0)'})
        },
        'rh.promocaocargo': {
            'Meta': {'object_name': 'PromocaoCargo'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'cargo_antigo': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cargo_antigo'", 'to': "orm['rh.Cargo']"}),
            'cargo_novo': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cargo_novo'", 'to': "orm['rh.Cargo']"}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 11, 4, 0, 0)'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.Funcionario']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'periodo_trabalhado': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.PeriodoTrabalhado']"})
        },
        'rh.promocaosalario': {
            'Meta': {'ordering': "['data_solicitacao']", 'object_name': 'PromocaoSalario'},
            'aprovado': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'autorizador': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'autorizador'", 'null': 'True', 'to': "orm['rh.Funcionario']"}),
            'avaliado': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'beneficiario': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'beneficiario'", 'to': "orm['rh.Funcionario']"}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data_resolucao': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'data_solicitacao': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 11, 4, 0, 0)'}),
            'descricao': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'observacao': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'periodo_trabalhado': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.PeriodoTrabalhado']"}),
            'solicitante': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'solicitante'", 'to': "orm['rh.Funcionario']"}),
            'valor': ('django.db.models.fields.FloatField', [], {})
        },
        'rh.solicitacaodelicenca': {
            'Meta': {'object_name': 'SolicitacaoDeLicenca'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data_autorizado': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'data_criado': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 11, 4, 0, 0)'}),
            'fim': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 11, 4, 0, 0)'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.Funcionario']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 11, 4, 0, 0)'}),
            'processado_por': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'autorizado_por'", 'null': 'True', 'to': "orm['rh.Funcionario']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'aberta'", 'max_length': '100'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['rh']