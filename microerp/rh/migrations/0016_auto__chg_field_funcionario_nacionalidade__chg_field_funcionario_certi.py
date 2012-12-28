# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Funcionario.nacionalidade'
        db.alter_column('rh_funcionario', 'nacionalidade', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.certificado_reservista'
        db.alter_column('rh_funcionario', 'certificado_reservista', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.escolaridade_serie_inconclusa'
        db.alter_column('rh_funcionario', 'escolaridade_serie_inconclusa', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.pis'
        db.alter_column('rh_funcionario', 'pis', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.rg_data'
        db.alter_column('rh_funcionario', 'rg_data', self.gf('django.db.models.fields.DateField')(null=True))

        # Changing field 'Funcionario.nome_pai'
        db.alter_column('rh_funcionario', 'nome_pai', self.gf('django.db.models.fields.CharField')(max_length=300, null=True))

        # Changing field 'Funcionario.nome'
        db.alter_column('rh_funcionario', 'nome', self.gf('django.db.models.fields.CharField')(max_length=300, null=True))

        # Changing field 'Funcionario.telefone_fixo'
        db.alter_column('rh_funcionario', 'telefone_fixo', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.observacao'
        db.alter_column('rh_funcionario', 'observacao', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Funcionario.rg_expeditor'
        db.alter_column('rh_funcionario', 'rg_expeditor', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.residencia'
        db.alter_column('rh_funcionario', 'residencia', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.carteira_profissional_serie'
        db.alter_column('rh_funcionario', 'carteira_profissional_serie', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.carteira_profissional_numero'
        db.alter_column('rh_funcionario', 'carteira_profissional_numero', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.rg'
        db.alter_column('rh_funcionario', 'rg', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.nascimento_dos_filhos'
        db.alter_column('rh_funcionario', 'nascimento_dos_filhos', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.nome_companheiro'
        db.alter_column('rh_funcionario', 'nome_companheiro', self.gf('django.db.models.fields.CharField')(max_length=300, null=True))

        # Changing field 'Funcionario.nome_mae'
        db.alter_column('rh_funcionario', 'nome_mae', self.gf('django.db.models.fields.CharField')(max_length=300, null=True))

        # Changing field 'Funcionario.carteira_habilitacao_categoria'
        db.alter_column('rh_funcionario', 'carteira_habilitacao_categoria', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.rua'
        db.alter_column('rh_funcionario', 'rua', self.gf('django.db.models.fields.CharField')(max_length=500, null=True))

        # Changing field 'Funcionario.sexo'
        db.alter_column('rh_funcionario', 'sexo', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.numero'
        db.alter_column('rh_funcionario', 'numero', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.cep'
        db.alter_column('rh_funcionario', 'cep', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.complemento'
        db.alter_column('rh_funcionario', 'complemento', self.gf('django.db.models.fields.CharField')(max_length=200, null=True))

        # Changing field 'Funcionario.carteira_habilitacao_vencimento'
        db.alter_column('rh_funcionario', 'carteira_habilitacao_vencimento', self.gf('django.db.models.fields.DateField')(null=True))

        # Changing field 'Funcionario.estado_civil'
        db.alter_column('rh_funcionario', 'estado_civil', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.carteira_habilitacao_numero'
        db.alter_column('rh_funcionario', 'carteira_habilitacao_numero', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.naturalidade'
        db.alter_column('rh_funcionario', 'naturalidade', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.telefone_celular'
        db.alter_column('rh_funcionario', 'telefone_celular', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.escolaridade_nivel'
        db.alter_column('rh_funcionario', 'escolaridade_nivel', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.cpf'
        db.alter_column('rh_funcionario', 'cpf', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Funcionario.titulo_eleitor'
        db.alter_column('rh_funcionario', 'titulo_eleitor', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Funcionario.valor_aluguel'
        db.alter_column('rh_funcionario', 'valor_aluguel', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'Funcionario.telefone_recado'
        db.alter_column('rh_funcionario', 'telefone_recado', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Funcionario.escolaridade_cursos'
        db.alter_column('rh_funcionario', 'escolaridade_cursos', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Funcionario.carteira_habilitacao_expedicao'
        db.alter_column('rh_funcionario', 'carteira_habilitacao_expedicao', self.gf('django.db.models.fields.DateField')(null=True))

    def backwards(self, orm):

        # Changing field 'Funcionario.nacionalidade'
        db.alter_column('rh_funcionario', 'nacionalidade', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'Funcionario.certificado_reservista'
        db.alter_column('rh_funcionario', 'certificado_reservista', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Funcionario.escolaridade_serie_inconclusa'
        db.alter_column('rh_funcionario', 'escolaridade_serie_inconclusa', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Funcionario.pis'
        db.alter_column('rh_funcionario', 'pis', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Funcionario.rg_data'
        db.alter_column('rh_funcionario', 'rg_data', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 12, 18, 0, 0)))

        # Changing field 'Funcionario.nome_pai'
        db.alter_column('rh_funcionario', 'nome_pai', self.gf('django.db.models.fields.CharField')(default='', max_length=300))

        # Changing field 'Funcionario.nome'
        db.alter_column('rh_funcionario', 'nome', self.gf('django.db.models.fields.CharField')(default='', max_length=300))

        # Changing field 'Funcionario.telefone_fixo'
        db.alter_column('rh_funcionario', 'telefone_fixo', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Funcionario.observacao'
        db.alter_column('rh_funcionario', 'observacao', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'Funcionario.rg_expeditor'
        db.alter_column('rh_funcionario', 'rg_expeditor', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Funcionario.residencia'
        db.alter_column('rh_funcionario', 'residencia', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Funcionario.carteira_profissional_serie'
        db.alter_column('rh_funcionario', 'carteira_profissional_serie', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Funcionario.carteira_profissional_numero'
        db.alter_column('rh_funcionario', 'carteira_profissional_numero', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Funcionario.rg'
        db.alter_column('rh_funcionario', 'rg', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Funcionario.nascimento_dos_filhos'
        db.alter_column('rh_funcionario', 'nascimento_dos_filhos', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Funcionario.nome_companheiro'
        db.alter_column('rh_funcionario', 'nome_companheiro', self.gf('django.db.models.fields.CharField')(default='', max_length=300))

        # Changing field 'Funcionario.nome_mae'
        db.alter_column('rh_funcionario', 'nome_mae', self.gf('django.db.models.fields.CharField')(default='', max_length=300))

        # Changing field 'Funcionario.carteira_habilitacao_categoria'
        db.alter_column('rh_funcionario', 'carteira_habilitacao_categoria', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Funcionario.rua'
        db.alter_column('rh_funcionario', 'rua', self.gf('django.db.models.fields.CharField')(default='', max_length=500))

        # Changing field 'Funcionario.sexo'
        db.alter_column('rh_funcionario', 'sexo', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Funcionario.numero'
        db.alter_column('rh_funcionario', 'numero', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Funcionario.cep'
        db.alter_column('rh_funcionario', 'cep', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Funcionario.complemento'
        db.alter_column('rh_funcionario', 'complemento', self.gf('django.db.models.fields.CharField')(default='', max_length=200))

        # Changing field 'Funcionario.carteira_habilitacao_vencimento'
        db.alter_column('rh_funcionario', 'carteira_habilitacao_vencimento', self.gf('django.db.models.fields.DateField')(default=''))

        # Changing field 'Funcionario.estado_civil'
        db.alter_column('rh_funcionario', 'estado_civil', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Funcionario.carteira_habilitacao_numero'
        db.alter_column('rh_funcionario', 'carteira_habilitacao_numero', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Funcionario.naturalidade'
        db.alter_column('rh_funcionario', 'naturalidade', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Funcionario.telefone_celular'
        db.alter_column('rh_funcionario', 'telefone_celular', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Funcionario.escolaridade_nivel'
        db.alter_column('rh_funcionario', 'escolaridade_nivel', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Funcionario.cpf'
        db.alter_column('rh_funcionario', 'cpf', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Funcionario.titulo_eleitor'
        db.alter_column('rh_funcionario', 'titulo_eleitor', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Funcionario.valor_aluguel'
        db.alter_column('rh_funcionario', 'valor_aluguel', self.gf('django.db.models.fields.FloatField')(default=' '))

        # Changing field 'Funcionario.telefone_recado'
        db.alter_column('rh_funcionario', 'telefone_recado', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'Funcionario.escolaridade_cursos'
        db.alter_column('rh_funcionario', 'escolaridade_cursos', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'Funcionario.carteira_habilitacao_expedicao'
        db.alter_column('rh_funcionario', 'carteira_habilitacao_expedicao', self.gf('django.db.models.fields.DateField')(default=' '))

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
            'departmento': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.Departamento']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'salario_referencia': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'rh.cursofuncionario': {
            'Meta': {'object_name': 'CursoFuncionario'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'carga_horaria': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 12, 18, 0, 0)'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.Funcionario']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'rh.departamento': {
            'Meta': {'object_name': 'Departamento'},
            'grupo_analista': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'grupo_analista'", 'null': 'True', 'to': "orm['auth.Group']"}),
            'grupo_responsavel': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'grupo_responsavel'", 'null': 'True', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'rh.experienciasprofissionaisfuncionario': {
            'Meta': {'object_name': 'ExperienciasProfissionaisFuncionario'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'cargo_final': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'cargo_inicial': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data_admissao': ('django.db.models.fields.DateField', [], {}),
            'data_demissao': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'emprego_atual': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'endereco_completo': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.Funcionario']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'motivo_saida': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'nome_da_empresa': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'telefone_fixo': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'ultimo_salario': ('django.db.models.fields.FloatField', [], {})
        },
        'rh.funcionario': {
            'Meta': {'ordering': "['nome']", 'object_name': 'Funcionario'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'bairro': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cadastro.Bairro']"}),
            'cargo_atual': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cargo_promovido'", 'null': 'True', 'to': "orm['rh.Cargo']"}),
            'cargo_inicial': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cargo_inicial'", 'to': "orm['rh.Cargo']"}),
            'carteira_habilitacao_categoria': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'carteira_habilitacao_expedicao': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'carteira_habilitacao_numero': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'carteira_habilitacao_vencimento': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'carteira_profissional_numero': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'carteira_profissional_serie': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'cep': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'certificado_reservista': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'cidade': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cadastro.Cidade']"}),
            'complemento': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'cpf': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'departamento': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.Departamento']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'escolaridade_conclusao': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 12, 18, 0, 0)'}),
            'escolaridade_cursos': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'escolaridade_nivel': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'escolaridade_serie_inconclusa': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'estado_civil': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'foto': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'funcionario_superior': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.Funcionario']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nacionalidade': ('django.db.models.fields.CharField', [], {'default': "'Brasil'", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'nascimento': ('django.db.models.fields.DateField', [], {}),
            'nascimento_dos_filhos': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'naturalidade': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'nome_companheiro': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'nome_mae': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'nome_pai': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'numero': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'observacao': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pis': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'possui_filhos': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'quantidade_filhos': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'residencia': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rg': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rg_data': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'rg_expeditor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rua': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'salario_atual': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'salario_inicial': ('django.db.models.fields.FloatField', [], {}),
            'sexo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'telefone_celular': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'telefone_fixo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'telefone_recado': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'titulo_eleitor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'valor_aluguel': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'rh.idiomafuncionario': {
            'Meta': {'object_name': 'IdiomaFuncionario'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.Funcionario']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idioma': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'instituicao': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'nivel': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'rh.periodotrabalhado': {
            'Meta': {'object_name': 'PeriodoTrabalhado'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'fim': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.Funcionario']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 12, 18, 0, 0)'})
        },
        'rh.promocaocargo': {
            'Meta': {'ordering': "['-criado']", 'object_name': 'PromocaoCargo'},
            'aprovado': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'autorizador': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'autorizacao_promocao_cargo_set'", 'null': 'True', 'to': "orm['rh.Funcionario']"}),
            'avaliado': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'beneficiario': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'promocao_cargo_set'", 'to': "orm['rh.Funcionario']"}),
            'cargo_antigo': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cargo_antigo'", 'to': "orm['rh.Cargo']"}),
            'cargo_novo': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cargo_novo'", 'to': "orm['rh.Cargo']"}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data_resolucao': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'data_solicitacao': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 12, 18, 0, 0)'}),
            'descricao': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'periodo_trabalhado': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.PeriodoTrabalhado']"}),
            'solicitante': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'solicitacao_promocao_cargo_set'", 'to': "orm['rh.Funcionario']"})
        },
        'rh.promocaosalario': {
            'Meta': {'ordering': "['data_solicitacao']", 'object_name': 'PromocaoSalario'},
            'aprovado': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'autorizador': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'autorizacao_promocao_salarial_set'", 'null': 'True', 'to': "orm['rh.Funcionario']"}),
            'avaliado': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'beneficiario': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'promocao_salarial_set'", 'to': "orm['rh.Funcionario']"}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data_resolucao': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'data_solicitacao': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 12, 18, 0, 0)'}),
            'descricao': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'observacao': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'periodo_trabalhado': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.PeriodoTrabalhado']"}),
            'solicitante': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'solicitacao_promocao_salarial_set'", 'to': "orm['rh.Funcionario']"}),
            'valor': ('django.db.models.fields.FloatField', [], {})
        },
        'rh.solicitacaodelicenca': {
            'Meta': {'object_name': 'SolicitacaoDeLicenca'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data_autorizado': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'data_criado': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 12, 18, 0, 0)'}),
            'fim': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 12, 18, 0, 0)'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.Funcionario']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 12, 18, 0, 0)'}),
            'processado_por': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'autorizado_por'", 'null': 'True', 'to': "orm['rh.Funcionario']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'aberta'", 'max_length': '100'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['rh']