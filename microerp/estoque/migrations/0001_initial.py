# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TipoDeProduto'
        db.create_table(u'estoque_tipodeproduto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'estoque', ['TipoDeProduto'])

        # Adding model 'Produto'
        db.create_table(u'estoque_produto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('codigo', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('codigo_barras', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('padrao_codigo_de_barras', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('descricao', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('unidade_de_venda', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('unidade_de_compra', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('fator', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('tipo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['estoque.TipoDeProduto'])),
            ('quantidade_em_estoque', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2)),
            ('preco_custo', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('preco_venda', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('tabela', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['estoque.TabelaDePreco'])),
            ('ncm', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('tributacao', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('substituicao_tributaria_valor', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('icms', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'estoque', ['Produto'])

        # Adding model 'TabelaDePreco'
        db.create_table(u'estoque_tabeladepreco', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('percentual', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'estoque', ['TabelaDePreco'])


    def backwards(self, orm):
        # Deleting model 'TipoDeProduto'
        db.delete_table(u'estoque_tipodeproduto')

        # Deleting model 'Produto'
        db.delete_table(u'estoque_produto')

        # Deleting model 'TabelaDePreco'
        db.delete_table(u'estoque_tabeladepreco')


    models = {
        u'estoque.produto': {
            'Meta': {'object_name': 'Produto'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'codigo': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'codigo_barras': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'descricao': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'fator': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'icms': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ncm': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'padrao_codigo_de_barras': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'preco_custo': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'preco_venda': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'quantidade_em_estoque': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'substituicao_tributaria_valor': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tabela': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['estoque.TabelaDePreco']"}),
            'tipo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['estoque.TipoDeProduto']"}),
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
            'percentual': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
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