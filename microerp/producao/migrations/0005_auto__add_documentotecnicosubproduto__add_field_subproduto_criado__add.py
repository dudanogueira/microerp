# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DocumentoTecnicoSubProduto'
        db.create_table(u'producao_documentotecnicosubproduto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subproduto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['producao.SubProduto'])),
            ('titulo', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('descricao', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('arquivo', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'producao', ['DocumentoTecnicoSubProduto'])

        # Adding field 'SubProduto.criado'
        db.add_column(u'producao_subproduto', 'criado',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True),
                      keep_default=False)

        # Adding field 'SubProduto.atualizado'
        db.add_column(u'producao_subproduto', 'atualizado',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True),
                      keep_default=False)

        # Adding field 'LinhaSubProduto.criado'
        db.add_column(u'producao_linhasubproduto', 'criado',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True),
                      keep_default=False)

        # Adding field 'LinhaSubProduto.atualizado'
        db.add_column(u'producao_linhasubproduto', 'atualizado',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True),
                      keep_default=False)

        # Adding field 'LinhaProdutoAvulso.criado'
        db.add_column(u'producao_linhaprodutoavulso', 'criado',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True),
                      keep_default=False)

        # Adding field 'LinhaProdutoAvulso.atualizado'
        db.add_column(u'producao_linhaprodutoavulso', 'atualizado',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True),
                      keep_default=False)

        # Adding field 'Produto.criado'
        db.add_column(u'producao_produto', 'criado',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True),
                      keep_default=False)

        # Adding field 'Produto.atualizado'
        db.add_column(u'producao_produto', 'atualizado',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'DocumentoTecnicoSubProduto'
        db.delete_table(u'producao_documentotecnicosubproduto')

        # Deleting field 'SubProduto.criado'
        db.delete_column(u'producao_subproduto', 'criado')

        # Deleting field 'SubProduto.atualizado'
        db.delete_column(u'producao_subproduto', 'atualizado')

        # Deleting field 'LinhaSubProduto.criado'
        db.delete_column(u'producao_linhasubproduto', 'criado')

        # Deleting field 'LinhaSubProduto.atualizado'
        db.delete_column(u'producao_linhasubproduto', 'atualizado')

        # Deleting field 'LinhaProdutoAvulso.criado'
        db.delete_column(u'producao_linhaprodutoavulso', 'criado')

        # Deleting field 'LinhaProdutoAvulso.atualizado'
        db.delete_column(u'producao_linhaprodutoavulso', 'atualizado')

        # Deleting field 'Produto.criado'
        db.delete_column(u'producao_produto', 'criado')

        # Deleting field 'Produto.atualizado'
        db.delete_column(u'producao_produto', 'atualizado')


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
        u'producao.documentotecnicosubproduto': {
            'Meta': {'object_name': 'DocumentoTecnicoSubProduto'},
            'arquivo': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'descricao': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subproduto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.SubProduto']"}),
            'titulo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
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
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'componente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.Componente']"}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'produto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.Produto']"}),
            'quantidade': ('django.db.models.fields.IntegerField', [], {}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'producao.linhasubproduto': {
            'Meta': {'object_name': 'LinhaSubProduto'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'componente_padrao': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subproduto_padrao_set'", 'on_delete': 'models.PROTECT', 'to': u"orm['producao.Componente']"}),
            'componentes_alternativos': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'subproduto_alternativo_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['producao.Componente']"}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
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
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'subprodutos': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['producao.SubProduto']", 'symmetrical': 'False'})
        },
        u'producao.subproduto': {
            'Meta': {'object_name': 'SubProduto'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'descricao': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imagem': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'possui_tags': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'subprodutos_agregados': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'subprodutos_agregados_rel_+'", 'null': 'True', 'to': u"orm['producao.SubProduto']"})
        }
    }

    complete_apps = ['producao']