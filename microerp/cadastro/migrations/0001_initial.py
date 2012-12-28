# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Cliente'
        db.create_table('cadastro_cliente', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=36, blank=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('tipo', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('cnpj', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('cpf', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('nascimento', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('ramo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cadastro.Ramo'])),
            ('observacao', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('origem', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cadastro.ClienteOrigem'])),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('telefone_fixo', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('telefone_celular', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('cidade', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cadastro.Cidade'])),
            ('bairro', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cadastro.Bairro'])),
            ('cep', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('rua', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('numero', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('complemento', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('criado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('atualizado', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal('cadastro', ['Cliente'])

        # Adding model 'Ramo'
        db.create_table('cadastro_ramo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('tipo', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('cadastro', ['Ramo'])

        # Adding model 'Cidade'
        db.create_table('cadastro_cidade', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('estado', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal('cadastro', ['Cidade'])

        # Adding model 'Bairro'
        db.create_table('cadastro_bairro', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('cidade', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cadastro.Cidade'])),
        ))
        db.send_create_signal('cadastro', ['Bairro'])

        # Adding model 'ClienteOrigem'
        db.create_table('cadastro_clienteorigem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nome', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('observacao', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('cadastro', ['ClienteOrigem'])


    def backwards(self, orm):
        # Deleting model 'Cliente'
        db.delete_table('cadastro_cliente')

        # Deleting model 'Ramo'
        db.delete_table('cadastro_ramo')

        # Deleting model 'Cidade'
        db.delete_table('cadastro_cidade')

        # Deleting model 'Bairro'
        db.delete_table('cadastro_bairro')

        # Deleting model 'ClienteOrigem'
        db.delete_table('cadastro_clienteorigem')


    models = {
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
        'cadastro.cliente': {
            'Meta': {'object_name': 'Cliente'},
            'atualizado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'bairro': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cadastro.Bairro']"}),
            'cep': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'cidade': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cadastro.Cidade']"}),
            'cnpj': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'complemento': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'cpf': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'criado': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nascimento': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'numero': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'observacao': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'origem': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cadastro.ClienteOrigem']"}),
            'ramo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cadastro.Ramo']"}),
            'rua': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'telefone_celular': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'telefone_fixo': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'})
        },
        'cadastro.clienteorigem': {
            'Meta': {'object_name': 'ClienteOrigem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'observacao': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'cadastro.ramo': {
            'Meta': {'object_name': 'Ramo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tipo': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['cadastro']