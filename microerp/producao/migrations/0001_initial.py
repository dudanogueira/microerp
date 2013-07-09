# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EstoqueFisico'
        db.create_table(u'producao_estoquefisico', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ativo', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('identificacao', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'producao', ['EstoqueFisico'])

        # Adding model 'PosicaoEstoque'
        db.create_table(u'producao_posicaoestoque', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data_entrada', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('nota_referecia', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['producao.NotaFiscal'], null=True, on_delete=models.PROTECT, blank=True)),
            ('componente', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['producao.Componente'])),
            ('estoque', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['producao.EstoqueFisico'])),
            ('quantidade', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('criado_por', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.User'], null=True, blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'producao', ['PosicaoEstoque'])

        # Adding model 'ComponenteTipo'
        db.create_table(u'producao_componentetipo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'producao', ['ComponenteTipo'])

        # Adding model 'LinhaFornecedorFabricanteComponente'
        db.create_table(u'producao_linhafornecedorfabricantecomponente', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('componente', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['producao.Componente'])),
            ('part_number_fornecedor', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('fornecedor', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fornecedor_componente_set', to=orm['producao.FabricanteFornecedor'])),
            ('part_number_fabricante', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('fabricante', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='fabricante_componente_set', null=True, to=orm['producao.FabricanteFornecedor'])),
        ))
        db.send_create_signal(u'producao', ['LinhaFornecedorFabricanteComponente'])

        # Adding unique constraint on 'LinhaFornecedorFabricanteComponente', fields ['componente', 'part_number_fornecedor', 'fornecedor']
        db.create_unique(u'producao_linhafornecedorfabricantecomponente', ['componente_id', 'part_number_fornecedor', 'fornecedor_id'])

        # Adding model 'Componente'
        db.create_table(u'producao_componente', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ativo', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('part_number', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('identificador', self.gf('django.db.models.fields.IntegerField')(default=1, null=True, blank=True)),
            ('tipo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['producao.ComponenteTipo'])),
            ('descricao', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('importado', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ncm', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('lead_time', self.gf('django.db.models.fields.IntegerField')()),
            ('preco_liquido_unitario_dolar', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2)),
            ('preco_liquido_unitario_real', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2)),
            ('preco_medio_unitario', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2)),
            ('quantidade_minima', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('medida', self.gf('django.db.models.fields.CharField')(default='un', max_length=100, blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'producao', ['Componente'])

        # Adding unique constraint on 'Componente', fields ['identificador', 'tipo']
        db.create_unique(u'producao_componente', ['identificador', 'tipo_id'])

        # Adding model 'FabricanteFornecedor'
        db.create_table(u'producao_fabricantefornecedor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tipo', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('ativo', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'producao', ['FabricanteFornecedor'])

        # Adding model 'LancamentoComponente'
        db.create_table(u'producao_lancamentocomponente', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nota', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['producao.NotaFiscal'])),
            ('part_number_fornecedor', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('quantidade', self.gf('django.db.models.fields.IntegerField')()),
            ('valor_unitario', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2)),
            ('impostos', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('componente', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['producao.Componente'], null=True, blank=True)),
            ('fabricante', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['producao.FabricanteFornecedor'], null=True, blank=True)),
            ('part_number_fabricante', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('aprender', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('valor_total_sem_imposto', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2)),
            ('valor_total_com_imposto', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2)),
            ('valor_taxa_diversa_proporcional', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2)),
            ('valor_unitario_final', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'producao', ['LancamentoComponente'])

        # Adding unique constraint on 'LancamentoComponente', fields ['part_number_fornecedor', 'componente', 'nota']
        db.create_unique(u'producao_lancamentocomponente', ['part_number_fornecedor', 'componente_id', 'nota_id'])

        # Adding unique constraint on 'LancamentoComponente', fields ['part_number_fornecedor', 'nota']
        db.create_unique(u'producao_lancamentocomponente', ['part_number_fornecedor', 'nota_id'])

        # Adding model 'NotaFiscal'
        db.create_table(u'producao_notafiscal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('numero', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('tipo', self.gf('django.db.models.fields.CharField')(default='n', max_length=1)),
            ('taxas_diversas', self.gf('django.db.models.fields.DecimalField')(default=0, null=True, max_digits=10, decimal_places=2, blank=True)),
            ('cotacao_dolar', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='a', max_length=100, blank=True)),
            ('fabricante_fornecedor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['producao.FabricanteFornecedor'])),
            ('data_entrada', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('total_sem_imposto', self.gf('django.db.models.fields.DecimalField')(default=0, null=True, max_digits=10, decimal_places=2, blank=True)),
            ('total_com_imposto', self.gf('django.db.models.fields.DecimalField')(default=0, null=True, max_digits=10, decimal_places=2, blank=True)),
            ('total_da_nota_em_dolar', self.gf('django.db.models.fields.DecimalField')(default=0, null=True, max_digits=10, decimal_places=2, blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'producao', ['NotaFiscal'])

        # Adding model 'SubProduto'
        db.create_table(u'producao_subproduto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('descricao', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('possui_tags', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'producao', ['SubProduto'])

        # Adding model 'LinhaSubProduto'
        db.create_table(u'producao_linhasubproduto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subproduto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['producao.SubProduto'])),
            ('componente_padrao', self.gf('django.db.models.fields.related.ForeignKey')(related_name='subproduto_padrao_set', to=orm['producao.Componente'])),
            ('quantidade', self.gf('django.db.models.fields.IntegerField')()),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'producao', ['LinhaSubProduto'])

        # Adding M2M table for field componentes_alternativos on 'LinhaSubProduto'
        db.create_table(u'producao_linhasubproduto_componentes_alternativos', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('linhasubproduto', models.ForeignKey(orm[u'producao.linhasubproduto'], null=False)),
            ('componente', models.ForeignKey(orm[u'producao.componente'], null=False))
        ))
        db.create_unique(u'producao_linhasubproduto_componentes_alternativos', ['linhasubproduto_id', 'componente_id'])

        # Adding model 'Produto'
        db.create_table(u'producao_produto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'producao', ['Produto'])

        # Adding M2M table for field subprodutos on 'Produto'
        db.create_table(u'producao_produto_subprodutos', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('produto', models.ForeignKey(orm[u'producao.produto'], null=False)),
            ('subproduto', models.ForeignKey(orm[u'producao.subproduto'], null=False))
        ))
        db.create_unique(u'producao_produto_subprodutos', ['produto_id', 'subproduto_id'])

        # Adding model 'LinhaProdutoAvulso'
        db.create_table(u'producao_linhaprodutoavulso', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('produto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['producao.Produto'])),
            ('componente', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['producao.Componente'])),
            ('quantidade', self.gf('django.db.models.fields.IntegerField')()),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'producao', ['LinhaProdutoAvulso'])


    def backwards(self, orm):
        # Removing unique constraint on 'LancamentoComponente', fields ['part_number_fornecedor', 'nota']
        db.delete_unique(u'producao_lancamentocomponente', ['part_number_fornecedor', 'nota_id'])

        # Removing unique constraint on 'LancamentoComponente', fields ['part_number_fornecedor', 'componente', 'nota']
        db.delete_unique(u'producao_lancamentocomponente', ['part_number_fornecedor', 'componente_id', 'nota_id'])

        # Removing unique constraint on 'Componente', fields ['identificador', 'tipo']
        db.delete_unique(u'producao_componente', ['identificador', 'tipo_id'])

        # Removing unique constraint on 'LinhaFornecedorFabricanteComponente', fields ['componente', 'part_number_fornecedor', 'fornecedor']
        db.delete_unique(u'producao_linhafornecedorfabricantecomponente', ['componente_id', 'part_number_fornecedor', 'fornecedor_id'])

        # Deleting model 'EstoqueFisico'
        db.delete_table(u'producao_estoquefisico')

        # Deleting model 'PosicaoEstoque'
        db.delete_table(u'producao_posicaoestoque')

        # Deleting model 'ComponenteTipo'
        db.delete_table(u'producao_componentetipo')

        # Deleting model 'LinhaFornecedorFabricanteComponente'
        db.delete_table(u'producao_linhafornecedorfabricantecomponente')

        # Deleting model 'Componente'
        db.delete_table(u'producao_componente')

        # Deleting model 'FabricanteFornecedor'
        db.delete_table(u'producao_fabricantefornecedor')

        # Deleting model 'LancamentoComponente'
        db.delete_table(u'producao_lancamentocomponente')

        # Deleting model 'NotaFiscal'
        db.delete_table(u'producao_notafiscal')

        # Deleting model 'SubProduto'
        db.delete_table(u'producao_subproduto')

        # Deleting model 'LinhaSubProduto'
        db.delete_table(u'producao_linhasubproduto')

        # Removing M2M table for field componentes_alternativos on 'LinhaSubProduto'
        db.delete_table('producao_linhasubproduto_componentes_alternativos')

        # Deleting model 'Produto'
        db.delete_table(u'producao_produto')

        # Removing M2M table for field subprodutos on 'Produto'
        db.delete_table('producao_produto_subprodutos')

        # Deleting model 'LinhaProdutoAvulso'
        db.delete_table(u'producao_linhaprodutoavulso')


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
        u'producao.componente': {
            'Meta': {'unique_together': "(('identificador', 'tipo'),)", 'object_name': 'Componente'},
            'ativo': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'descricao': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identificador': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'importado': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lead_time': ('django.db.models.fields.IntegerField', [], {}),
            'medida': ('django.db.models.fields.CharField', [], {'default': "'un'", 'max_length': '100', 'blank': 'True'}),
            'ncm': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'part_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'preco_liquido_unitario_dolar': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'preco_liquido_unitario_real': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'preco_medio_unitario': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'quantidade_minima': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'tipo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.ComponenteTipo']"})
        },
        u'producao.componentetipo': {
            'Meta': {'object_name': 'ComponenteTipo'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'producao.estoquefisico': {
            'Meta': {'object_name': 'EstoqueFisico'},
            'ativo': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identificacao': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'producao.fabricantefornecedor': {
            'Meta': {'object_name': 'FabricanteFornecedor'},
            'ativo': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'producao.lancamentocomponente': {
            'Meta': {'unique_together': "(('part_number_fornecedor', 'componente', 'nota'), ('part_number_fornecedor', 'nota'))", 'object_name': 'LancamentoComponente'},
            'aprender': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'componente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.Componente']", 'null': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'fabricante': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.FabricanteFornecedor']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'impostos': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'nota': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.NotaFiscal']"}),
            'part_number_fabricante': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'part_number_fornecedor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'quantidade': ('django.db.models.fields.IntegerField', [], {}),
            'valor_taxa_diversa_proporcional': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'valor_total_com_imposto': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'valor_total_sem_imposto': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'valor_unitario': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'valor_unitario_final': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'})
        },
        u'producao.linhafornecedorfabricantecomponente': {
            'Meta': {'unique_together': "(('componente', 'part_number_fornecedor', 'fornecedor'),)", 'object_name': 'LinhaFornecedorFabricanteComponente'},
            'componente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.Componente']"}),
            'fabricante': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'fabricante_componente_set'", 'null': 'True', 'to': u"orm['producao.FabricanteFornecedor']"}),
            'fornecedor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fornecedor_componente_set'", 'to': u"orm['producao.FabricanteFornecedor']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'part_number_fabricante': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'part_number_fornecedor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'producao.linhaprodutoavulso': {
            'Meta': {'object_name': 'LinhaProdutoAvulso'},
            'componente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.Componente']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'produto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.Produto']"}),
            'quantidade': ('django.db.models.fields.IntegerField', [], {}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'producao.linhasubproduto': {
            'Meta': {'object_name': 'LinhaSubProduto'},
            'componente_padrao': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subproduto_padrao_set'", 'to': u"orm['producao.Componente']"}),
            'componentes_alternativos': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'subproduto_alternativo_set'", 'symmetrical': 'False', 'to': u"orm['producao.Componente']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quantidade': ('django.db.models.fields.IntegerField', [], {}),
            'subproduto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.SubProduto']"}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'producao.notafiscal': {
            'Meta': {'object_name': 'NotaFiscal'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'cotacao_dolar': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data_entrada': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'fabricante_fornecedor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.FabricanteFornecedor']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'numero': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'a'", 'max_length': '100', 'blank': 'True'}),
            'taxas_diversas': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'default': "'n'", 'max_length': '1'}),
            'total_com_imposto': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'total_da_nota_em_dolar': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'total_sem_imposto': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'})
        },
        u'producao.posicaoestoque': {
            'Meta': {'ordering': "('-criado', '-id')", 'object_name': 'PosicaoEstoque'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'componente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.Componente']"}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'criado_por': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['account.User']", 'null': 'True', 'blank': 'True'}),
            'data_entrada': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'estoque': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.EstoqueFisico']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nota_referecia': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.NotaFiscal']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'quantidade': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'producao.produto': {
            'Meta': {'object_name': 'Produto'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'subprodutos': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['producao.SubProduto']", 'symmetrical': 'False'})
        },
        u'producao.subproduto': {
            'Meta': {'object_name': 'SubProduto'},
            'descricao': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'possui_tags': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        }
    }

    complete_apps = ['producao']