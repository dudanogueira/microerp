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
__version__ = '2.0.0'

from django.contrib import admin

from comercial.models import PropostaComercial
from comercial.models import Orcamento
from comercial.models import LinhaRecursoMaterial
from comercial.models import LinhaRecursoHumano
from comercial.models import TipoRecursoLogistico
from comercial.models import LinhaRecursoLogistico
from comercial.models import PerfilAcessoComercial
from comercial.models import ContratoFechado
from comercial.models import TipodeContratoFechado
from comercial.models import CategoriaContratoFechado
from comercial.models import FollowUpDePropostaComercial
from comercial.models import RequisicaoDeProposta
from comercial.models import GrupoIndicadorDeProdutoProposto
from comercial.models import SubGrupoIndicadorDeProdutoProposto
from comercial.models import FechamentoDeComissao
from comercial.models import LancamentoDeFechamentoComissao
from comercial.models import TabelaDeComissao
from comercial.models import TipoDeProposta
from comercial.models import TabelaDeParcelamento
from comercial.models import ClasseTipoDeProposta
from comercial.models import EmpresaComercial
from financeiro.models import LancamentoFinanceiroReceber
from comercial.models import DocumentoGerado
from comercial.models import GrupoDocumento
from comercial.models import ItemGrupoDocumento

# ADMIN ACTIONS
def lancar_contrato(modeladmin, request, queryset):
    for contrato in queryset:
        contrato.lancar()
lancar_contrato.short_description = u"Lançar Contrato para o Financeiro"

class PerfilAcessoComercialAdmin(admin.ModelAdmin):
    list_display = 'user', 'gerente', 'analista', 'super_gerente', 'empresa'
    list_filter = 'empresa',

class FollowUpPropostaInlineAdmin(admin.StackedInline):
    model = FollowUpDePropostaComercial
    extra = 0

class LinhaRecursoLogisticoInlineAdmin(admin.StackedInline):
    model = LinhaRecursoLogistico
    extra = 0

class PropostaComercialAdmin(admin.ModelAdmin):
    list_display  = 'id', 'cliente', 'precliente', 'valor_proposto','data_expiracao', 'status', 'expirada', 'contrato_id'
    list_filter = 'probabilidade', 'data_expiracao', 'status'
    search_fields = 'cliente__nome', 'precliente__nome'
    list_display_links = list_display
    inlines = [FollowUpPropostaInlineAdmin, LinhaRecursoLogisticoInlineAdmin]

class LinhaRecursoMaterialInLine(admin.TabularInline):
    raw_id_fields = ("produto",)
    model = LinhaRecursoMaterial
    extra = 1

class LinhaRecursoHumanoInLine(admin.TabularInline):
    model = LinhaRecursoHumano
    extra = 1

class OrcamentoAdmin(admin.ModelAdmin):
    inlines = [LinhaRecursoMaterialInLine, LinhaRecursoHumanoInLine]
    list_filter = 'modelo', 'ativo', 'promocao', 'tabelado'
    list_display = 'descricao', 'ativo', 'modelo', 'promocao', 'tabelado'
    
class LancamentoFinanceiroReceberInline(admin.TabularInline):
    model = LancamentoFinanceiroReceber
    extra = 0

class ContratoFechadoAdmin(admin.ModelAdmin):
    list_display = 'id', 'cliente', 'valor', 'status', 'responsavel', 'proposta_id'
    list_filter = 'tipo', 'status',
    search_fields = 'cliente__nome', 'id'
    inlines = [LancamentoFinanceiroReceberInline]
    actions = [lancar_contrato,]
    date_hierarchy = 'criado'

class TipodeContratoFechadoAdmin(admin.ModelAdmin):
    pass

class FollowUpDePropostaComercialAdmin(admin.ModelAdmin):
    date_hierarchy = 'criado'

class FechamentoDeComissaoAdmin(admin.ModelAdmin):
    pass

class LancamentoDeFechamentoComissaoAdmin(admin.ModelAdmin):
    pass

class TabelaDeComissaoAdmin(admin.ModelAdmin):
    list_display = 'valor_inicio', 'valor_fim', 'porcentagem'

class EmpresaComercialAdmin(admin.ModelAdmin):
    list_display = 'nome', 'nome_reduzido', 'principal'
    search_fields = 'nome',

class GrupoDocumentoInline(admin.StackedInline):
    model = GrupoDocumento
    extra = 0

class ItemGrupoDocumentoInline(admin.StackedInline):
    model = ItemGrupoDocumento
    extra = 0

class DocumentoGeradoAdmin(admin.ModelAdmin):
    inlines = [GrupoDocumentoInline,]
    list_filter = 'modelo',

class GrupoDocumentoAdmin(admin.ModelAdmin):
    inlines = [ItemGrupoDocumentoInline,]
    list_filter = 'documento__modelo',

admin.site.register(PropostaComercial, PropostaComercialAdmin)
admin.site.register(Orcamento, OrcamentoAdmin)
admin.site.register(PerfilAcessoComercial, PerfilAcessoComercialAdmin)
admin.site.register(ContratoFechado, ContratoFechadoAdmin)
admin.site.register(TipodeContratoFechado, TipodeContratoFechadoAdmin)
admin.site.register(CategoriaContratoFechado)
admin.site.register(FollowUpDePropostaComercial, FollowUpDePropostaComercialAdmin)
admin.site.register(RequisicaoDeProposta)
admin.site.register(GrupoIndicadorDeProdutoProposto)
admin.site.register(SubGrupoIndicadorDeProdutoProposto)
admin.site.register(FechamentoDeComissao, FechamentoDeComissaoAdmin)
admin.site.register(LancamentoDeFechamentoComissao, LancamentoDeFechamentoComissaoAdmin)
admin.site.register(TabelaDeComissao, TabelaDeComissaoAdmin)
admin.site.register(TipoDeProposta)
admin.site.register(TipoRecursoLogistico)
admin.site.register(LinhaRecursoLogistico)
admin.site.register(LinhaRecursoHumano)
admin.site.register(TabelaDeParcelamento)
admin.site.register(ClasseTipoDeProposta)
admin.site.register(EmpresaComercial, EmpresaComercialAdmin)
admin.site.register(DocumentoGerado, DocumentoGeradoAdmin)
admin.site.register(GrupoDocumento, GrupoDocumentoAdmin)
admin.site.register(ItemGrupoDocumento)