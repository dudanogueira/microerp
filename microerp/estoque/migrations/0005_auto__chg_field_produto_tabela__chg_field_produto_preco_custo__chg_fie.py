# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Produto.tabela'
        db.alter_column(u'estoque_produto', 'tabela_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['estoque.TabelaDePreco'], null=True))

        # Changing field 'Produto.preco_custo'
        db.alter_column(u'estoque_produto', 'preco_custo', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2))

        # Changing field 'Produto.preco_venda'
        db.alter_column(u'estoque_produto', 'preco_venda', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2))

    def backwards(self, orm):

        # Changing field 'Produto.tabela'
        db.alter_column(u'estoque_produto', 'tabela_id', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['estoque.TabelaDePreco']))

        # Changing field 'Produto.preco_custo'
        db.alter_column(u'estoque_produto', 'preco_custo', self.gf('django.db.models.fields.DecimalField')(default=1, max_digits=10, decimal_places=2))

        # Changing field 'Produto.preco_venda'
        db.alter_column(u'estoque_produto', 'preco_venda', self.gf('django.db.models.fields.DecimalField')(default=1, max_digits=10, decimal_places=2))

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
        u'estoque.codigodebarra': {
            'Meta': {'object_name': 'CodigoDeBarra'},
            'codigo_barras': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'padrao_codigo_de_barras': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'produto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['estoque.Produto']"})
        },
        u'estoque.perfilacessoestoque': {
            'Meta': {'object_name': 'PerfilAcessoEstoque'},
            'analista': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'gerente': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['account.User']", 'unique': 'True'})
        },
        u'estoque.produto': {
            'Meta': {'object_name': 'Produto'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'codigo': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'descricao': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'fator': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'icms': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ncm': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'preco_custo': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'preco_venda': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'quantidade_em_estoque': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'substituicao_tributaria_valor': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tabela': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['estoque.TabelaDePreco']", 'null': 'True', 'blank': 'True'}),
            'tipo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['estoque.TipoDeProduto']", 'null': 'True', 'blank': 'True'}),
            'tributacao': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'unidade_de_compra': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'unidade_de_venda': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'estoque.tabeladepreco': {
            'Meta': {'object_name': 'TabelaDePreco'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'percentual': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'})
        },
        u'estoque.tipodeproduto': {
            'Meta': {'object_name': 'TipoDeProduto'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['estoque']