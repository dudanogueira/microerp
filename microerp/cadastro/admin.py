# -*- coding: utf-8 -*-
"""This file is part of the microerp project.

This program is free software: you can redistribute it and/or modify it 
under the terms of the GNU Lesser General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

__author__ = 'Duda Nogueira <dudanogueira@gmail.com>'
__copyright__ = 'Copyright (c) 2012 Duda Nogueira'
__version__ = '0.0.1'

from django.contrib import admin

from cadastro.models import Cliente, Cidade, Bairro, Ramo, ClienteOrigem, ConsultaDeCredito, TipoDeConsultaDeCredito

from comercial.models import SolicitacaoComercial

from georefs.models import ReferenciaGeograficaCliente

from django import forms

from olwidget.admin import GeoModelAdmin

class SolicitacaoComercialInline(admin.TabularInline):
    model = SolicitacaoComercial
    ordering = ['criado']
    extra = 0

class ConsultaDeCreditoInline(admin.TabularInline):
    model = ConsultaDeCredito
    ordering = ['criado']
    extra = 0

class ClienteAdmin(admin.ModelAdmin):
    list_filter = ('tipo', 'cidade', 'bairro')
    search_fields = ('nome', 'cpf', 'cnpj', 'rua', 'bairro__nome')
    list_display = ('nome', 'documento')
    list_display_links = list_display
    date_hierarchy = "criado"
    readonly_fields = ['criado', 'atualizado', 'uuid']
    fieldsets = (
            (u"Informações Gerais", {
                'classes': ('wide', 'extrapretty'),
                'fields': ('nome', 'tipo', 'ramo', 'nascimento', 'observacao')
            }),
            (u"Documentos", {
                'classes': ('wide', 'extrapretty'),
                'fields': ('cnpj', 'cpf', 'inscricao_estadual', 'rg',)
            }),
            (u'Contato', {
                'classes': ('wide', 'extrapretty'),
                'fields': ('contato', 'email', 'telefone_fixo', 'telefone_celular', 'fax')
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
    inlines = [ConsultaDeCreditoInline, SolicitacaoComercialInline]


class ReferenciaGeograficaClienteAdmin(GeoModelAdmin):
    list_filter= 'cliente__tipo', 'cliente__cidade', 'cliente__cidade__estado'

admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Cidade)
admin.site.register(Bairro)
admin.site.register(Ramo)
admin.site.register(ClienteOrigem)
admin.site.register(TipoDeConsultaDeCredito)
admin.site.register(ReferenciaGeograficaCliente, ReferenciaGeograficaClienteAdmin)
