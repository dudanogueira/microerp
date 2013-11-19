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
__copyright__ = 'Copyright (c) 2013 Duda Nogueira'
__version__ = '0.0.1'

from django.contrib import admin

from cadastro.models import Cliente, Cidade, Bairro, Ramo, ClienteOrigem, ConsultaDeCredito, TipoDeConsultaDeCredito
from cadastro.models import PerfilAcessoRecepcao
from cadastro.models import PreCliente
from cadastro.models import PerfilClienteLogin
from cadastro.models import Recado
from cadastro.models import EnderecoCliente
from cadastro.models import EnderecoEmpresa

from django import forms

class ConsultaDeCreditoInline(admin.TabularInline):
    model = ConsultaDeCredito
    ordering = ['criado']
    extra = 0

class EnderecoClienteInline(admin.StackedInline):
    model = EnderecoCliente
    ordering = ['criado']
    extra = 0

class ClienteAdmin(admin.ModelAdmin):
    save_on_top = True
    list_filter = ('tipo',)
    search_fields = ('nome', 'cpf', 'cnpj',)
    list_display = ('nome', 'documento')
    list_display_links = list_display
    date_hierarchy = "criado"
    readonly_fields = ['criado', 'atualizado', 'uuid']
    fieldsets_a = (
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
            (u'Meta Informações', {
                'classes': ('wide', 'extrapretty', 'collapse'),
                'fields': ('criado', 'atualizado', 'uuid')
            }),
        )
    inlines = [EnderecoClienteInline, ConsultaDeCreditoInline]

class PerfilAcessoRecepcaoAdmin(admin.ModelAdmin):
    list_filter = 'user', 'analista', 'gerente',
    list_display = 'user',  'analista', 'gerente',

class PreClienteAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = 'id', 'nome', 'contato', 'dados'
    list_display_links = list_display
    date_hierarchy = "criado"

class RecadoAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = 'id', 'lido', 'destinatario', 'remetente', 'adicionado_por', 'criado', 'cliente'
    list_display_links = list_display
    date_hierarchy = "criado"
    list_filter = 'destinatario', 'remetente', 'adicionado_por'

class CidadeAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('nome', 'estado')
    list_display = 'id', 'nome', 'estado'

class BairroAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ('nome', 'cidade__nome')
    list_display = 'id', 'nome', 'cidade'

class PerfilClienteLoginAdmin(admin.ModelAdmin):
    search_fields = ('cliente__nome', 'cliente__cpf', 'cliente__cnpj', 'cliente__user')
    list_display = 'cliente', 'user'
    raw_id_fields = 'cliente',

admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Cidade, CidadeAdmin)
admin.site.register(Bairro, BairroAdmin)
admin.site.register(Ramo)
admin.site.register(ClienteOrigem)
admin.site.register(TipoDeConsultaDeCredito)
admin.site.register(PerfilAcessoRecepcao, PerfilAcessoRecepcaoAdmin)
admin.site.register(PreCliente, PreClienteAdmin)
admin.site.register(Recado, RecadoAdmin)
admin.site.register(PerfilClienteLogin, PerfilClienteLoginAdmin)
admin.site.register(EnderecoEmpresa)