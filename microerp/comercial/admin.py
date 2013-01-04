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

from comercial.models import SolicitacaoComercial, TipoSolicitacaoComercial, ContatoComercial, TipoContatoComercial, FonteDeAgendaComercial

class SolicitacaoComercialAdmin(admin.ModelAdmin):
    list_filter = ('status', 'tipo__mao_de_obra_inclusa', 'cliente__bairro__nome',  'cliente__cidade__nome', 'cliente__cidade__estado',)
    list_display = ('identificador', 'cliente', 'tipo', 'valor_calculado', 'status')
    list_display_links = list_display
    search_fields = ['id', 'cliente__nome', 'cliente__cpf', 'cliente__cnpj', 'cliente__telefone_fixo', 'cliente__telefone_celular',]
    
class TipoSolicitacaoComercialAdmin(admin.ModelAdmin):
    list_filter = ('mao_de_obra_inclusa', 'permite_valor_variavel',)

class ContatoComercialAdmin(admin.ModelAdmin):
    date_hierarchy = "inicio"
    list_display = ('nome', 'status', 'inicio', 'fim', 'cliente')
    search_fields = ['id', 'cliente__nome', 'cliente__cpf', 'cliente__cnpj', 'cliente__telefone_fixo', 'cliente__telefone_celular', 'cliente__rua', 'cliente__bairro__nome']
    list_filter = ('funcionario', 'inicio', 'status', 'cliente__cidade__nome', 'cliente__bairro__nome')
    list_display_links = list_display

admin.site.register(SolicitacaoComercial, SolicitacaoComercialAdmin)
admin.site.register(TipoSolicitacaoComercial, TipoSolicitacaoComercialAdmin)
admin.site.register(ContatoComercial, ContatoComercialAdmin)
admin.site.register(TipoContatoComercial)
admin.site.register(FonteDeAgendaComercial)