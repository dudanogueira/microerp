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

from comercial.models import PropostaComercial
from comercial.models import Orcamento
from comercial.models import LinhaRecursoMaterial
from comercial.models import LinhaRecursoHumano
from comercial.models import PerfilAcessoComercial
from comercial.models import ContratoFechado
from comercial.models import TipodeContratoFechado
from comercial.models import CategoriaContratoFechado
from comercial.models import Marca
from comercial.models import Modelo
from comercial.models import QuantidadeDeMarca
from comercial.models import FollowUpDePropostaComercial


# ADMIN ACTIONS
def lancar_contrato(modeladmin, request, queryset):
    for contrato in queryset:
        contrato.lancar()
lancar_contrato.short_description = u"Lançar Contrato para o Financeiro"


class PerfilAcessoComercialAdmin(admin.ModelAdmin):
    pass

class PropostaComercialAdmin(admin.ModelAdmin):
    pass

class LinhaRecursoMaterialInLine(admin.TabularInline):
    raw_id_fields = ("produto",)
    model = LinhaRecursoMaterial
    extra = 0

class LinhaRecursoHumanoInLine(admin.TabularInline):
    model = LinhaRecursoHumano
    extra = 0

class OrcamentoAdmin(admin.ModelAdmin):
    inlines = [LinhaRecursoMaterialInLine, LinhaRecursoHumanoInLine]

class QuantidadeDeMarcaInline(admin.StackedInline):
    model = QuantidadeDeMarca
    extra = 0
    

class ContratoFechadoAdmin(admin.ModelAdmin):
    list_filter = 'tipo', 'status',
    search_fields = 'cliente__nome', 
    inlines = [QuantidadeDeMarcaInline]
    actions = [lancar_contrato,]

class TipodeContratoFechadoAdmin(admin.ModelAdmin):
    pass

class FollowUpDePropostaComercialAdmin(admin.ModelAdmin):
    date_hierarchy = 'data'

admin.site.register(PropostaComercial, PropostaComercialAdmin)
admin.site.register(Orcamento, OrcamentoAdmin)
admin.site.register(PerfilAcessoComercial, PerfilAcessoComercialAdmin)
admin.site.register(ContratoFechado, ContratoFechadoAdmin)
admin.site.register(TipodeContratoFechado, TipodeContratoFechadoAdmin)
admin.site.register(CategoriaContratoFechado)
admin.site.register(Marca)
admin.site.register(Modelo)
admin.site.register(FollowUpDePropostaComercial, FollowUpDePropostaComercialAdmin)