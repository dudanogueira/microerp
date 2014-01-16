# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding M2M table for field sub_grupo_indicador on 'Produto'
        db.create_table(u'estoque_produto_sub_grupo_indicador', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('produto', models.ForeignKey(orm[u'estoque.produto'], null=False)),
            ('subgrupoindicadordeprodutoproposto', models.ForeignKey(orm[u'comercial.subgrupoindicadordeprodutoproposto'], null=False))
        ))
        db.create_unique(u'estoque_produto_sub_grupo_indicador', ['produto_id', 'subgrupoindicadordeprodutoproposto_id'])


        # Changing field 'Produto.grupo_indicador'
        db.alter_column(u'estoque_produto', 'grupo_indicador_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['comercial.GrupoIndicadorDeProdutoProposto'], null=True))

    def backwards(self, orm):
        # Removing M2M table for field sub_grupo_indicador on 'Produto'
        db.delete_table('estoque_produto_sub_grupo_indicador')


        # Changing field 'Produto.grupo_indicador'
        db.alter_column(u'estoque_produto', 'grupo_indicador_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['comercial.GrupoIndicadorDeProdutoVendido'], null=True))

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
        u'comercial.grupoindicadordeprodutoproposto': {
            'Meta': {'object_name': 'GrupoIndicadorDeProdutoProposto'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'comercial.subgrupoindicadordeprodutoproposto': {
            'Meta': {'object_name': 'SubGrupoIndicadorDeProdutoProposto'},
            'grupo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['comercial.GrupoIndicadorDeProdutoProposto']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'estoque.produto': {
            'Meta': {'object_name': 'Produto'},
            'ativo': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'codigo': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'descricao': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'fator': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'grupo_indicador': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['comercial.GrupoIndicadorDeProdutoProposto']", 'null': 'True', 'blank': 'True'}),
            'icms': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ncm': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'preco_consumo': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'preco_custo': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'preco_venda': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'quantidade_em_estoque': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'sub_grupo_indicador': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['comercial.SubGrupoIndicadorDeProdutoProposto']", 'null': 'True', 'blank': 'True'}),
            'substituicao_tributaria_valor': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tabela': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['estoque.TabelaDePreco']", 'null': 'True', 'blank': 'True'}),
            'tipo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['estoque.TipoDeProduto']", 'null': 'True', 'blank': 'True'}),
            'tributacao': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'unidade_de_compra': ('django.db.models.fields.CharField', [], {'default': "'un'", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'unidade_de_venda': ('django.db.models.fields.CharField', [], {'default': "'un'", 'max_length': '100', 'null': 'True', 'blank': 'True'})
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