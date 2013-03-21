# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Funcionario'
        db.create_table(u'rh_funcionario', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=36, blank=True)),
            ('foto', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['account.User'], unique=True, null=True, blank=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('residencia', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('valor_aluguel', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('nascimento', self.gf('django.db.models.fields.DateField')()),
            ('observacao', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('sexo', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('naturalidade', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('nacionalidade', self.gf('django.db.models.fields.CharField')(default='Brasil', max_length=100, null=True, blank=True)),
            ('estado_civil', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('nome_companheiro', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('nome_pai', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('nome_mae', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('rg', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rg_data', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('rg_expeditor', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('cpf', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('carteira_profissional_numero', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('carteira_profissional_serie', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('carteira_profissional_emissao', self.gf('django.db.models.fields.DateField')(blank=True)),
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
            ('escolaridade_conclusao', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 3, 18, 0, 0))),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('telefone_fixo', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('telefone_celular', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('telefone_recado', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('bairro', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cadastro.Bairro'])),
            ('cep', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rua', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
            ('numero', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('complemento', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('salario_inicial', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('salario_atual', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('valor_hora', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('forma_de_pagamento', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('gratificacao', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('numero_lre', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('cargo_inicial', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cargo_inicial', to=orm['rh.Cargo'])),
            ('cargo_atual', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='cargo_promovido', null=True, to=orm['rh.Cargo'])),
            ('funcionario_superior', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Funcionario'], null=True, blank=True)),
            ('local_de_trabalho', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('membro_cipa', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'rh', ['Funcionario'])

        # Adding model 'IdiomaFuncionario'
        db.create_table(u'rh_idiomafuncionario', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('funcionario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Funcionario'])),
            ('idioma', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('nivel', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('instituicao', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'rh', ['IdiomaFuncionario'])

        # Adding model 'CursoFuncionario'
        db.create_table(u'rh_cursofuncionario', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('funcionario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Funcionario'])),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('data', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 3, 18, 0, 0))),
            ('carga_horaria', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'rh', ['CursoFuncionario'])

        # Adding model 'ExperienciasProfissionaisFuncionario'
        db.create_table(u'rh_experienciasprofissionaisfuncionario', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('funcionario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Funcionario'])),
            ('emprego_atual', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('nome_da_empresa', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('telefone_fixo', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('endereco_completo', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('data_admissao', self.gf('django.db.models.fields.DateField')()),
            ('data_demissao', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('cargo_inicial', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('cargo_final', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('ultimo_salario', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('motivo_saida', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'rh', ['ExperienciasProfissionaisFuncionario'])

        # Adding model 'Cargo'
        db.create_table(u'rh_cargo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('descricao', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('salario_referencia', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('departmento', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Departamento'])),
            ('periculosidade', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('gratificacao', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('dias_renovacao_exames', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'rh', ['Cargo'])

        # Adding M2M table for field exame_medico_padrao on 'Cargo'
        db.create_table(u'rh_cargo_exame_medico_padrao', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('cargo', models.ForeignKey(orm[u'rh.cargo'], null=False)),
            ('tipodeexamemedico', models.ForeignKey(orm[u'rh.tipodeexamemedico'], null=False))
        ))
        db.create_unique(u'rh_cargo_exame_medico_padrao', ['cargo_id', 'tipodeexamemedico_id'])

        # Adding model 'Departamento'
        db.create_table(u'rh_departamento', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'rh', ['Departamento'])

        # Adding model 'PeriodoTrabalhado'
        db.create_table(u'rh_periodotrabalhado', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('funcionario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Funcionario'])),
            ('inicio', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 3, 18, 0, 0))),
            ('fim', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'rh', ['PeriodoTrabalhado'])

        # Adding model 'PromocaoSalario'
        db.create_table(u'rh_promocaosalario', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('aprovado', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('avaliado', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('descricao', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('data_solicitacao', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 3, 18, 0, 0))),
            ('data_resolucao', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('beneficiario', self.gf('django.db.models.fields.related.ForeignKey')(related_name='promocao_salarial_set', to=orm['rh.Funcionario'])),
            ('solicitante', self.gf('django.db.models.fields.related.ForeignKey')(related_name='solicitacao_promocao_salarial_set', to=orm['rh.Funcionario'])),
            ('autorizador', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='autorizacao_promocao_salarial_set', null=True, to=orm['rh.Funcionario'])),
            ('valor', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('periodo_trabalhado', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.PeriodoTrabalhado'])),
            ('observacao', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'rh', ['PromocaoSalario'])

        # Adding model 'PromocaoCargo'
        db.create_table(u'rh_promocaocargo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('avaliado', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('aprovado', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('descricao', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('data_solicitacao', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 3, 18, 0, 0))),
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
        db.send_create_signal(u'rh', ['PromocaoCargo'])

        # Adding model 'SolicitacaoDeLicenca'
        db.create_table(u'rh_solicitacaodelicenca', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('funcionario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Funcionario'])),
            ('motivo', self.gf('django.db.models.fields.TextField')()),
            ('inicio', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 3, 18, 0, 0))),
            ('fim', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 3, 18, 0, 0))),
            ('status', self.gf('django.db.models.fields.CharField')(default='aberta', max_length=100)),
            ('tipo', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('data_criado', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 3, 18, 0, 0))),
            ('data_autorizado', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('processado_por', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='autorizado_por', null=True, to=orm['rh.Funcionario'])),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'rh', ['SolicitacaoDeLicenca'])

        # Adding model 'FolhaDePonto'
        db.create_table(u'rh_folhadeponto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('funcionario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Funcionario'])),
            ('data_referencia', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 3, 18, 0, 0))),
            ('encerrado', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('autorizado', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('funcionario_autorizador', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='folhadeponto_autorizado_set', null=True, to=orm['rh.Funcionario'])),
            ('arquivo', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'rh', ['FolhaDePonto'])

        # Adding model 'EntradaFolhaDePonto'
        db.create_table(u'rh_entradafolhadeponto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('folha', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.FolhaDePonto'])),
            ('hora', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('tipo', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'rh', ['EntradaFolhaDePonto'])

        # Adding model 'DependenteDeFuncionario'
        db.create_table(u'rh_dependentedefuncionario', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('relacao', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('nascimento', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 3, 18, 0, 0))),
            ('funcionario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Funcionario'])),
        ))
        db.send_create_signal(u'rh', ['DependenteDeFuncionario'])

        # Adding model 'TipoDeExameMedico'
        db.create_table(u'rh_tipodeexamemedico', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('descricao', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('valor', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
        ))
        db.send_create_signal(u'rh', ['TipoDeExameMedico'])

        # Adding model 'RotinaExameMedico'
        db.create_table(u'rh_rotinaexamemedico', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('tipo', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('funcionario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rh.Funcionario'])),
        ))
        db.send_create_signal(u'rh', ['RotinaExameMedico'])

        # Adding M2M table for field exames on 'RotinaExameMedico'
        db.create_table(u'rh_rotinaexamemedico_exames', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('rotinaexamemedico', models.ForeignKey(orm[u'rh.rotinaexamemedico'], null=False)),
            ('tipodeexamemedico', models.ForeignKey(orm[u'rh.tipodeexamemedico'], null=False))
        ))
        db.create_unique(u'rh_rotinaexamemedico_exames', ['rotinaexamemedico_id', 'tipodeexamemedico_id'])

        # Adding model 'PerfilAcessoRH'
        db.create_table(u'rh_perfilacessorh', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('gerente', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('analista', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['account.User'], unique=True)),
        ))
        db.send_create_signal(u'rh', ['PerfilAcessoRH'])


    def backwards(self, orm):
        # Deleting model 'Funcionario'
        db.delete_table(u'rh_funcionario')

        # Deleting model 'IdiomaFuncionario'
        db.delete_table(u'rh_idiomafuncionario')

        # Deleting model 'CursoFuncionario'
        db.delete_table(u'rh_cursofuncionario')

        # Deleting model 'ExperienciasProfissionaisFuncionario'
        db.delete_table(u'rh_experienciasprofissionaisfuncionario')

        # Deleting model 'Cargo'
        db.delete_table(u'rh_cargo')

        # Removing M2M table for field exame_medico_padrao on 'Cargo'
        db.delete_table('rh_cargo_exame_medico_padrao')

        # Deleting model 'Departamento'
        db.delete_table(u'rh_departamento')

        # Deleting model 'PeriodoTrabalhado'
        db.delete_table(u'rh_periodotrabalhado')

        # Deleting model 'PromocaoSalario'
        db.delete_table(u'rh_promocaosalario')

        # Deleting model 'PromocaoCargo'
        db.delete_table(u'rh_promocaocargo')

        # Deleting model 'SolicitacaoDeLicenca'
        db.delete_table(u'rh_solicitacaodelicenca')

        # Deleting model 'FolhaDePonto'
        db.delete_table(u'rh_folhadeponto')

        # Deleting model 'EntradaFolhaDePonto'
        db.delete_table(u'rh_entradafolhadeponto')

        # Deleting model 'DependenteDeFuncionario'
        db.delete_table(u'rh_dependentedefuncionario')

        # Deleting model 'TipoDeExameMedico'
        db.delete_table(u'rh_tipodeexamemedico')

        # Deleting model 'RotinaExameMedico'
        db.delete_table(u'rh_rotinaexamemedico')

        # Removing M2M table for field exames on 'RotinaExameMedico'
        db.delete_table('rh_rotinaexamemedico_exames')

        # Deleting model 'PerfilAcessoRH'
        db.delete_table(u'rh_perfilacessorh')


    models = {
        u'account.user': {
            'Meta': {'object_name': 'User'},
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '100', 'blank': 'True'})
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
            'departmento': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Departamento']"}),
            'descricao': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dias_renovacao_exames': ('django.db.models.fields.IntegerField', [], {}),
            'exame_medico_padrao': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['rh.TipoDeExameMedico']", 'symmetrical': 'False'}),
            'gratificacao': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'periculosidade': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'salario_referencia': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        },
        u'rh.cursofuncionario': {
            'Meta': {'object_name': 'CursoFuncionario'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'carga_horaria': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 3, 18, 0, 0)'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Funcionario']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'rh.departamento': {
            'Meta': {'object_name': 'Departamento'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'rh.dependentedefuncionario': {
            'Meta': {'object_name': 'DependenteDeFuncionario'},
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Funcionario']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nascimento': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 3, 18, 0, 0)'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'relacao': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'rh.entradafolhadeponto': {
            'Meta': {'object_name': 'EntradaFolhaDePonto'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'folha': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.FolhaDePonto']"}),
            'hora': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'rh.experienciasprofissionaisfuncionario': {
            'Meta': {'object_name': 'ExperienciasProfissionaisFuncionario'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'cargo_final': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'cargo_inicial': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data_admissao': ('django.db.models.fields.DateField', [], {}),
            'data_demissao': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'emprego_atual': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'endereco_completo': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Funcionario']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'motivo_saida': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'nome_da_empresa': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'telefone_fixo': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'ultimo_salario': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        },
        u'rh.folhadeponto': {
            'Meta': {'object_name': 'FolhaDePonto'},
            'arquivo': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'autorizado': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data_referencia': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 3, 18, 0, 0)'}),
            'encerrado': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Funcionario']"}),
            'funcionario_autorizador': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'folhadeponto_autorizado_set'", 'null': 'True', 'to': u"orm['rh.Funcionario']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'rh.funcionario': {
            'Meta': {'ordering': "['nome']", 'object_name': 'Funcionario'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'bairro': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cadastro.Bairro']"}),
            'cargo_atual': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cargo_promovido'", 'null': 'True', 'to': u"orm['rh.Cargo']"}),
            'cargo_inicial': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cargo_inicial'", 'to': u"orm['rh.Cargo']"}),
            'carteira_habilitacao_categoria': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'carteira_habilitacao_expedicao': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'carteira_habilitacao_numero': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'carteira_habilitacao_vencimento': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'carteira_profissional_emissao': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            'carteira_profissional_numero': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'carteira_profissional_serie': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'cep': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'certificado_reservista': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'complemento': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'cpf': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'escolaridade_conclusao': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 3, 18, 0, 0)'}),
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
            'pis': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'residencia': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rg': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rg_data': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'rg_expeditor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'rua': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'salario_atual': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'salario_inicial': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'sexo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'telefone_celular': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'telefone_fixo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'telefone_recado': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'titulo_eleitor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['account.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'valor_aluguel': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'valor_hora': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        },
        u'rh.idiomafuncionario': {
            'Meta': {'object_name': 'IdiomaFuncionario'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Funcionario']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idioma': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'instituicao': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'nivel': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'rh.perfilacessorh': {
            'Meta': {'object_name': 'PerfilAcessoRH'},
            'analista': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'gerente': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['account.User']", 'unique': 'True'})
        },
        u'rh.periodotrabalhado': {
            'Meta': {'object_name': 'PeriodoTrabalhado'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'fim': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Funcionario']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 3, 18, 0, 0)'})
        },
        u'rh.promocaocargo': {
            'Meta': {'ordering': "['-criado']", 'object_name': 'PromocaoCargo'},
            'aprovado': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'autorizador': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'autorizacao_promocao_cargo_set'", 'null': 'True', 'to': u"orm['rh.Funcionario']"}),
            'avaliado': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'beneficiario': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'promocao_cargo_set'", 'to': u"orm['rh.Funcionario']"}),
            'cargo_antigo': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cargo_antigo'", 'to': u"orm['rh.Cargo']"}),
            'cargo_novo': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cargo_novo'", 'to': u"orm['rh.Cargo']"}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data_resolucao': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'data_solicitacao': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 3, 18, 0, 0)'}),
            'descricao': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'periodo_trabalhado': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.PeriodoTrabalhado']"}),
            'solicitante': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'solicitacao_promocao_cargo_set'", 'to': u"orm['rh.Funcionario']"})
        },
        u'rh.promocaosalario': {
            'Meta': {'ordering': "['data_solicitacao']", 'object_name': 'PromocaoSalario'},
            'aprovado': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'autorizador': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'autorizacao_promocao_salarial_set'", 'null': 'True', 'to': u"orm['rh.Funcionario']"}),
            'avaliado': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'beneficiario': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'promocao_salarial_set'", 'to': u"orm['rh.Funcionario']"}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data_resolucao': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'data_solicitacao': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 3, 18, 0, 0)'}),
            'descricao': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'observacao': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'periodo_trabalhado': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.PeriodoTrabalhado']"}),
            'solicitante': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'solicitacao_promocao_salarial_set'", 'to': u"orm['rh.Funcionario']"}),
            'valor': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        },
        u'rh.rotinaexamemedico': {
            'Meta': {'object_name': 'RotinaExameMedico'},
            'data': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'exames': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['rh.TipoDeExameMedico']", 'symmetrical': 'False'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Funcionario']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'rh.solicitacaodelicenca': {
            'Meta': {'object_name': 'SolicitacaoDeLicenca'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data_autorizado': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'data_criado': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 3, 18, 0, 0)'}),
            'fim': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 3, 18, 0, 0)'}),
            'funcionario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rh.Funcionario']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inicio': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 3, 18, 0, 0)'}),
            'motivo': ('django.db.models.fields.TextField', [], {}),
            'processado_por': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'autorizado_por'", 'null': 'True', 'to': u"orm['rh.Funcionario']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'aberta'", 'max_length': '100'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'rh.tipodeexamemedico': {
            'Meta': {'object_name': 'TipoDeExameMedico'},
            'descricao': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'valor': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        }
    }

    complete_apps = ['rh']