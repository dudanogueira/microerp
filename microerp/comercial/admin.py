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


import csv
import xlwt
from django.http import HttpResponse

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
from comercial.models import TipoDeProposta, TipoDePropostaDadoVariavel
from comercial.models import TabelaDeParcelamento
from comercial.models import ClasseTipoDeProposta
from comercial.models import EmpresaComercial
from financeiro.models import LancamentoFinanceiroReceber
from comercial.models import DocumentoGerado
from comercial.models import GrupoDocumento
from comercial.models import ItemGrupoDocumento
from comercial.models import GrupoDadosVariaveis
from comercial.models import DadoVariavel
from comercial.models import MotivoFechamentoProposta

# ADMIN ACTIONS

def export_xls(modeladmin, request, queryset):

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=mymodel.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Contrato")

    row_num = 0

    columns = [
        (u"ID", 2000),
        (u"Cliente", 6000),
        (u"Valor", 8000),
        (u"Tipo", 8000),
        (u"Criação Proposta", 8000),
        (u"Criação Contrato", 8000),
        (u"Vendedor", 8000),
        (u"Status", 8000),
        (u"Cidade", 8000),
        (u"Telefone", 8000),
        (u"Empresa", 8000),
        (u"Follow Up", 8000),
    ]

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    font_style = xlwt.XFStyle()
    font_style.alignment.wrap = 1

    for obj in queryset:
        row_num += 1
        if obj.cliente.endereco_principal():
            cidade = obj.cliente.endereco_principal().cidade_texto
        else:
            cidade = ''
        if obj.propostacomercial.tipo:
            tipo = obj.propostacomercial.tipo.nome
        else:
            tipo = ''
        row = [
            obj.pk,
            obj.cliente.nome,
            obj.valor,
            tipo,
            obj.propostacomercial.criado.strftime("%d/%m/%Y"),
            obj.criado.strftime("%d/%m/%Y"),
            obj.responsavel.nome,
            obj.get_status_display(),
            cidade,
            "%s - %s" % (obj.cliente.telefone_celular, obj.cliente.telefone_fixo),
            obj.responsavel.user.perfilacessocomercial.empresa.nome,
            obj.propostacomercial.followupdepropostacomercial_set.count(),
        ]
        for col_num in xrange(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

export_xls.short_description = u"Export XLS"

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


def export_xls_proposta(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=mymodel.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Contrato")

    row_num = 0

    columns = [
        (u"ID", 2000),
        (u"Cliente", 6000),
        (u"PRE CLIENTE", 6000),
        (u"Valor", 8000),
        (u"Tipo", 8000),
        (u"Criação Proposta", 8000),
        (u"Criação Contrato", 8000),
        (u"Data Declínio", 8000),
        (u"Motivo", 8000),
        (u"Motivo Opção", 8000),
        (u"Responsável (Vendedor)", 8000),
        (u"Status", 8000),
        (u"Cidade", 8000),
        (u"Telefone", 8000),
        (u"Empresa", 8000),
        (u"Follow Up", 8000),
    ]

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    font_style = xlwt.XFStyle()
    font_style.alignment.wrap = 1

    # para cada proposta
    for obj in queryset:
        row_num += 1
        if obj.cliente and obj.cliente.endereco_principal():
            cidade = obj.cliente.endereco_principal().cidade_texto
        else:
            cidade = ''
        if obj.tipo:
            tipo = obj.tipo.nome
        else:
            tipo = ''
        cliente = ''
        precliente = ''
        definido_perdido = ''
        if obj.cliente:
            cliente = obj.cliente.nome
        if obj.precliente:
            precliente = obj.precliente.nome
        if obj.definido_perdido_em:
            definido_perdido = obj.definido_perdido_em.strftime("%d/%m/%Y")
        if cliente:
            telefones = "%s - %s" % (obj.cliente.telefone_celular, obj.cliente.telefone_fixo)
        else:
            telefones = "%s - %s" % (obj.precliente.telefone_celular, obj.precliente.telefone_fixo)
        nome_designado = ''
        empresa_designado = ''

        if obj.designado:
            nome_designado = obj.designado.nome
            if obj.designado.user.perfilacessocomercial:
                empresa_designado = obj.designado.user.perfilacessocomercial.empresa.nome

        row = [
            obj.pk,
            cliente,
            precliente,
            obj.valor_proposto,
            tipo,
            obj.criado.strftime("%d/%m/%Y"),
            obj.criado.strftime("%d/%m/%Y"),
            definido_perdido,
            obj.definido_perdido_motivo,
            getattr(obj.definido_perdido_motivo_opcao, 'nome', ''),
            nome_designado,
            obj.get_status_display(),
            cidade,
            telefones,
            empresa_designado,
            obj.followupdepropostacomercial_set.count(),
        ]
        for col_num in xrange(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

export_xls_proposta.short_description = u"Exportar para Excel (.xls)"



class PropostaComercialAdmin(admin.ModelAdmin):
    list_display  = 'id', 'cliente', 'precliente', 'valor_proposto','data_expiracao', 'status', 'expirada', 'contrato_id'
    list_filter = 'probabilidade', 'data_expiracao', 'status'
    search_fields = 'cliente__nome', 'precliente__nome'
    list_display_links = list_display
    inlines = [FollowUpPropostaInlineAdmin, LinhaRecursoLogisticoInlineAdmin]
    actions = [export_xls_proposta]

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
    list_filter = 'tipo', 'status', 'categoria__nome'
    search_fields = 'cliente__nome', 'id'
    inlines = [LancamentoFinanceiroReceberInline]
    actions = [lancar_contrato, export_xls]
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
    list_filter = 'modelo', 'tipo'
    search_fields = 'propostacomercial__id', 'contratofechado__id',

class GrupoDocumentoAdmin(admin.ModelAdmin):
    inlines = [ItemGrupoDocumentoInline,]
    list_filter = 'documento__modelo', 'documento__tipo'
    search_fields = 'documento__propostacomercial__id', 'documento__contratofechado__id'

class DadoVariavelInline(admin.StackedInline):
    model = DadoVariavel
    extra = 0

class GrupoDadosVariaveisAdmin(admin.ModelAdmin):
    search_fields = 'documento__contratofechado__id', 'documento__propostacomercial__id'
    list_filter = 'documento__tipo', 'documento__modelo'
    inlines = DadoVariavelInline,


class TipoDePropostaDadoVariavelInline(admin.StackedInline):
    model = TipoDePropostaDadoVariavel
    extra = 0

class TipoPropostaAdmin(admin.ModelAdmin):
    inlines = [TipoDePropostaDadoVariavelInline,]
    pass


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
admin.site.register(TipoDeProposta, TipoPropostaAdmin)
admin.site.register(TipoDePropostaDadoVariavel)
admin.site.register(TipoRecursoLogistico)
admin.site.register(LinhaRecursoLogistico)
admin.site.register(LinhaRecursoHumano)
admin.site.register(TabelaDeParcelamento)
admin.site.register(ClasseTipoDeProposta)
admin.site.register(EmpresaComercial, EmpresaComercialAdmin)
admin.site.register(DocumentoGerado, DocumentoGeradoAdmin)
admin.site.register(GrupoDocumento, GrupoDocumentoAdmin)
admin.site.register(ItemGrupoDocumento)
admin.site.register(GrupoDadosVariaveis, GrupoDadosVariaveisAdmin)
admin.site.register(DadoVariavel)
admin.site.register(MotivoFechamentoProposta)
