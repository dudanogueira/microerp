# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'PosicaoEstoque.quantidade_alterada'
        db.add_column(u'producao_posicaoestoque', 'quantidade_alterada',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True),
                      keep_default=False)

        # Adding field 'FabricanteFornecedor.rua'
        db.add_column(u'producao_fabricantefornecedor', 'rua',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True),
                      keep_default=False)

        # Adding field 'FabricanteFornecedor.numero'
        db.add_column(u'producao_fabricantefornecedor', 'numero',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True),
                      keep_default=False)

        # Adding field 'FabricanteFornecedor.bairro'
        db.add_column(u'producao_fabricantefornecedor', 'bairro',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True),
                      keep_default=False)

        # Adding field 'FabricanteFornecedor.cep'
        db.add_column(u'producao_fabricantefornecedor', 'cep',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True),
                      keep_default=False)

        # Adding field 'FabricanteFornecedor.cidade'
        db.add_column(u'producao_fabricantefornecedor', 'cidade',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True),
                      keep_default=False)

        # Adding field 'FabricanteFornecedor.estado'
        db.add_column(u'producao_fabricantefornecedor', 'estado',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True),
                      keep_default=False)

        # Adding field 'FabricanteFornecedor.telefone'
        db.add_column(u'producao_fabricantefornecedor', 'telefone',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'PosicaoEstoque.quantidade_alterada'
        db.delete_column(u'producao_posicaoestoque', 'quantidade_alterada')

        # Deleting field 'FabricanteFornecedor.rua'
        db.delete_column(u'producao_fabricantefornecedor', 'rua')

        # Deleting field 'FabricanteFornecedor.numero'
        db.delete_column(u'producao_fabricantefornecedor', 'numero')

        # Deleting field 'FabricanteFornecedor.bairro'
        db.delete_column(u'producao_fabricantefornecedor', 'bairro')

        # Deleting field 'FabricanteFornecedor.cep'
        db.delete_column(u'producao_fabricantefornecedor', 'cep')

        # Deleting field 'FabricanteFornecedor.cidade'
        db.delete_column(u'producao_fabricantefornecedor', 'cidade')

        # Deleting field 'FabricanteFornecedor.estado'
        db.delete_column(u'producao_fabricantefornecedor', 'estado')

        # Deleting field 'FabricanteFornecedor.telefone'
        db.delete_column(u'producao_fabricantefornecedor', 'telefone')


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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'producao.componente': {
            'Meta': {'unique_together': "(('identificador', 'tipo'),)", 'object_name': 'Componente'},
            'ativo': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'descricao': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identificador': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'lead_time': ('django.db.models.fields.IntegerField', [], {}),
            'medida': ('django.db.models.fields.CharField', [], {'default': "'un'", 'max_length': '100', 'blank': 'True'}),
            'nacionalidade': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'ncm': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'part_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'preco_liquido_unitario_dolar': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'preco_liquido_unitario_real': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'preco_medio_unitario': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'tipo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.ComponenteTipo']"})
        },
        u'producao.componentetipo': {
            'Meta': {'object_name': 'ComponenteTipo'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '3'})
        },
        u'producao.documentotecnicoproduto': {
            'Meta': {'object_name': 'DocumentoTecnicoProduto'},
            'arquivo': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'descricao': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'produto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.ProdutoFinal']"}),
            'titulo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
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
            'bairro': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'cep': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'cidade': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'cnpj': ('django.db.models.fields.CharField', [], {'max_length': '400', 'blank': 'True'}),
            'contatos': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'estado': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'numero': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'rua': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'telefone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'producao.lancamentocomponente': {
            'Meta': {'ordering': "('peso', 'nota')", 'unique_together': "(('part_number_fornecedor', 'componente', 'nota'), ('part_number_fornecedor', 'nota'))", 'object_name': 'LancamentoComponente'},
            'aprender': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'componente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.Componente']", 'null': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'fabricante': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.FabricanteFornecedor']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'impostos': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'nota': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.NotaFiscal']"}),
            'part_number_fabricante': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'part_number_fornecedor': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'peso': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'quantidade': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
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
            'produto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.ProdutoFinal']"}),
            'quantidade': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'producao.linhasubproduto': {
            'Meta': {'object_name': 'LinhaSubProduto'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'peso': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'subproduto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.SubProduto']"}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'producao.linhasubprodutoagregado': {
            'Meta': {'object_name': 'LinhaSubProdutoAgregado'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quantidade': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'subproduto_agregado': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'linhasubproutos_escolhidos'", 'to': u"orm['producao.SubProduto']"}),
            'subproduto_principal': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'linhasubprodutos_agregados'", 'to': u"orm['producao.SubProduto']"})
        },
        u'producao.notafiscal': {
            'Meta': {'unique_together': "(('fabricante_fornecedor', 'numero'),)", 'object_name': 'NotaFiscal'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'cotacao_dolar': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'data_entrada': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'data_lancado_estoque': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'fabricante_fornecedor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.FabricanteFornecedor']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lancado_por': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'numero': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'a'", 'max_length': '100', 'blank': 'True'}),
            'taxas_diversas': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'total_com_imposto': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'total_da_nota_em_dolar': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'total_sem_imposto': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'})
        },
        u'producao.opcaolinhasubproduto': {
            'Meta': {'unique_together': "(('linha', 'padrao'),)", 'object_name': 'OpcaoLinhaSubProduto'},
            'componente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.Componente']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'linha': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.LinhaSubProduto']"}),
            'padrao': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'quantidade': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        },
        u'producao.perfilacessoproducao': {
            'Meta': {'object_name': 'PerfilAcessoProducao'},
            'analista': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'gerente': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'producao.posicaoestoque': {
            'Meta': {'ordering': "('-criado', '-id')", 'object_name': 'PosicaoEstoque'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'componente': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.Componente']"}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'criado_por': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'data_entrada': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'estoque': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.EstoqueFisico']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'justificativa': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'nota_referencia': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['producao.NotaFiscal']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'quantidade': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2'}),
            'quantidade_alterada': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'producao.produtofinal': {
            'Meta': {'object_name': 'ProdutoFinal'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'descricao': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imagem': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
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
            'possui_tags': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        }
    }

    complete_apps = ['producao']