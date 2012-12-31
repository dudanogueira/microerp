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
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('residencia', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('valor_aluguel', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('nascimento', self.gf('django.db.models.fields.DateField')()),
            ('observacao', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('sexo', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('naturalidade', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('nacionalidade', self.gf('django.db.models.fields.CharField')(default='Brasil', max_length=100, null=True, blank=True)),
            ('estado_civil', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('possui_filhos', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('quantidade_filhos', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('nascimento_dos_filhos', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('nome_companheiro', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('nome_pai', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('nome_mae', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('rg', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rg_data', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('rg_expeditor', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('cpf', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('carteira_profissional_numero', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('carteira_profissional_serie', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('titulo_eleitor', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('pis', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('certificado_reservista', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('carteira_habilitacao_numero', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('carteira_habilitacao_categoria', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('carteira_habilitacao_vencimento', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('carteira_habilitacao_expedicao', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('escolaridade_nivel', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('escolaridade_cursos', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('escolaridade_serie_inconclusa', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('escolaridade_conclusao', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 12, 30, 0, 0))),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('telefone_fixo', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('telefone_celular', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('telefone_recado', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('bairro', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cadastro.Bairro'])),
            ('cep', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rua', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
            ('numero', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('complemento', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('salario_inicial', self.gf('django.db.models.fields.FloatField')()),
            ('salario_atual', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('valor_hora', self.gf('django.db.models.fields.FloatField')()),
            ('cargo_inicial', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cargo_inicial', to=orm['rh.Cargo'])),
            ('cargo_atual', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='cargo_promovido', null=True, to=orm['rh.Cargo'])),
            ('departamento', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Departamento'])),
            ('funcionario_superior', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Funcionario'], null=True, blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal('rh', ['Funcionario'])

        # Adding model 'IdiomaFuncionario'
        db.create_table('rh_idiomafuncionario', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('funcionario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Funcionario'])),
            ('idioma', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('nivel', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('instituicao', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal('rh', ['IdiomaFuncionario'])

        # Adding model 'CursoFuncionario'
        db.create_table('rh_cursofuncionario', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('funcionario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Funcionario'])),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('data', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 12, 30, 0, 0))),
            ('carga_horaria', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal('rh', ['CursoFuncionario'])

        # Adding model 'ExperienciasProfissionaisFuncionario'
        db.create_table('rh_experienciasprofissionaisfuncionario', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('funcionario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Funcionario'])),
            ('emprego_atual', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('nome_da_empresa', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('telefone_fixo', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('endereco_completo', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('data_admissao', self.gf('django.db.models.fields.DateField')()),
            ('data_demissao', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('cargo_inicial', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('cargo_final', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('ultimo_salario', self.gf('django.db.models.fields.FloatField')()),
            ('motivo_saida', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal('rh', ['ExperienciasProfissionaisFuncionario'])

        # Adding model 'Cargo'
        db.create_table('rh_cargo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('salario_referencia', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('departmento', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Departamento'])),
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
            ('inicio', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 12, 30, 0, 0))),
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
            ('data_solicitacao', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 12, 30, 0, 0))),
            ('data_resolucao', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('beneficiario', self.gf('django.db.models.fields.related.ForeignKey')(related_name='promocao_salarial_set', to=orm['rh.Funcionario'])),
            ('solicitante', self.gf('django.db.models.fields.related.ForeignKey')(related_name='solicitacao_promocao_salarial_set', to=orm['rh.Funcionario'])),
            ('autorizador', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='autorizacao_promocao_salarial_set', null=True, to=orm['rh.Funcionario'])),
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
            ('avaliado', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('aprovado', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('descricao', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('data_solicitacao', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 12, 30, 0, 0))),
            ('data_resolucao', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('beneficiario', self.gf('django.db.models.fields.related.ForeignKey')(related_name='promocao_cargo_set', to=orm['rh.Funcionario'])),
            ('solicitante', self.gf('django.db.models.fields.related.ForeignKey')(related_name='solicitacao_promocao_cargo_set', to=orm['rh.Funcionario'])),
            ('autorizador', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='autorizacao_promocao_cargo_set', null=True, to=orm['rh.Funcionario'])),
            ('cargo_antigo', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cargo_antigo', to=orm['rh.Cargo'])),
            ('cargo_novo', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cargo_novo', to=orm['rh.Cargo'])),
            ('periodo_trabalhado', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.PeriodoTrabalhado'])),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal('rh', ['PromocaoCargo'])

        # Adding model 'SolicitacaoDeLicenca'
        db.create_table('rh_solicitacaodelicenca', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('funcionario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Funcionario'])),
            ('inicio', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 12, 30, 0, 0))),
            ('fim', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 12, 30, 0, 0))),
            ('status', self.gf('django.db.models.fields.CharField')(default='aberta', max_length=100)),
            ('tipo', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('data_criado', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 12, 30, 0, 0))),
            ('data_autorizado', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('processado_por', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='autorizado_por', null=True, to=orm['rh.Funcionario'])),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal('rh', ['SolicitacaoDeLicenca'])

        # Adding model 'FolhaDePonto'
        db.create_table('rh_folhadeponto', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('funcionario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Funcionario'])),
            ('data_referencia', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 12, 30, 0, 0))),
            ('encerrado', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('autorizado', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('funcionario_autorizador', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='folhadeponto_autorizado_set', null=True, to=orm['rh.Funcionario'])),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal('rh', ['FolhaDePonto'])

        # Adding model 'EntradaFolhaDePonto'
        db.create_table('rh_entradafolhadeponto', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('folha', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.FolhaDePonto'])),
            ('hora_entrada', self.gf('django.db.models.fields.DateTimeField')()),
            ('hora_saida', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('rh', ['EntradaFolhaDePonto'])


    def backwards(self, orm):
        # Deleting model 'Funcionario'
        db.delete_table('rh_funcionario')

        # Deleting model 'IdiomaFuncionario'
        db.delete_table('rh_idiomafuncionario')

        # Deleting model 'CursoFuncionario'
        db.delete_table('rh_cursofuncionario')

        # Deleting model 'ExperienciasProfissionaisFuncionario'
        db.delete_table('rh_experienciasprofissionaisfuncionario')

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

        # Deleting model 'FolhaDePonto'
        db.delete_table('rh_folhadeponto')

        # Deleting model 'EntradaFolhaDePonto'
        db.delete_table('rh_entradafolhadeponto')


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
            'data': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 12, 30, 0, 0)'}),
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
        'rh.entradafolhadeponto': {
            'Meta': {'object_name': 'EntradaFolhaDePonto'},
            'folha': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.FolhaDePonto']"}),
            'hora_entrada': ('django.db.models.fields.DateTimeField', [], {}),
            'hora_saida': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
        'rh.folhadeponto': {
            'Meta': {'object_name': 'FolhaDePonto'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'autorizado': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data_referencia': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 12, 30, 0, 0)'}),
            'encerrado': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.Funcionario']"}),
            'funcionario_autorizador': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'folhadeponto_autorizado_set'", 'null': 'True', 'to': "orm['rh.Funcionario']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
            'complemento': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'cpf': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'departamento': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.Departamento']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'escolaridade_conclusao': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 12, 30, 0, 0)'}),
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
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
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
            'valor_aluguel': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'valor_hora': ('django.db.models.fields.FloatField', [], {})
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
            'inicio': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 12, 30, 0, 0)'})
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
            'data_solicitacao': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 12, 30, 0, 0)'}),
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
            'data_solicitacao': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 12, 30, 0, 0)'}),
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
            'data_criado': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 12, 30, 0, 0)'}),
            'fim': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 12, 30, 0, 0)'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rh.Funcionario']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 12, 30, 0, 0)'}),
            'processado_por': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'autorizado_por'", 'null': 'True', 'to': "orm['rh.Funcionario']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'aberta'", 'max_length': '100'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['rh']