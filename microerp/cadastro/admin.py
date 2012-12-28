# -*- coding: utf-8 -*-
from django.contrib import admin

from cadastro.models import Cliente, Cidade, Bairro, Ramo, ClienteOrigem

from comercial.models import SolicitacaoComercial

from django import forms

class SolicitacaoComercialInline(admin.TabularInline):
    model = SolicitacaoComercial
    ordering = ['criado']
    extra = 0

class ClienteAdmin(admin.ModelAdmin):
    list_filter = ('tipo', 'cidade')
    search_fields = ('nome', 'cpf', 'cnpj')
    list_display = ('nome', 'documento')
    list_display_links = list_display
    date_hierarchy = "criado"
    readonly_fields = ['criado', 'atualizado', 'uuid']
    fieldsets = (
            (u"Informações Gerais", {
                'classes': ('wide', 'extrapretty'),
                'fields': ('nome', 'tipo', 'ramo', 'cnpj', 'cpf', 'nascimento', 'observacao')
            }),
            (u'Contato', {
                'classes': ('wide', 'extrapretty'),
                'fields': ('email', 'telefone_fixo', 'telefone_celular', 'fax')
            }),
            (u'Sistema', {
                'classes': ('wide', 'extrapretty'),
                'fields': ('funcionario_responsavel',)
            }),            
            (u'Marketing', {
                'classes': ('wide', 'extrapretty'),
                'fields': ('origem',)
            }),
            (u'Endereço', {
                'classes': ('wide', 'extrapretty'),
                'fields': ('cidade', 'bairro', 'cep', 'rua', 'numero', 'complemento')
            }),
            (u'Meta Informações', {
                'classes': ('wide', 'extrapretty', 'collapse'),
                'fields': ('criado', 'atualizado', 'uuid')
            }),
        )
    inlines = [SolicitacaoComercialInline]

admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Cidade)
admin.site.register(Bairro)
admin.site.register(Ramo)
admin.site.register(ClienteOrigem)
