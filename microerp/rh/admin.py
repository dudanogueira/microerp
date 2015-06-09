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

from rh.models import Funcionario
from rh.models import Cargo
from rh.models import Departamento
from rh.models import PeriodoTrabalhado
from rh.models import PromocaoSalario
from rh.models import PromocaoCargo
from rh.models import SolicitacaoDeLicenca
from rh.models import ExperienciasProfissionaisFuncionario
from rh.models import IdiomaFuncionario
from rh.models import CursoFuncionario
from rh.models import FolhaDePonto
from rh.models import EntradaFolhaDePonto
from rh.models import DependenteDeFuncionario
from rh.models import TipoDeExameMedico
from rh.models import RotinaExameMedico
from rh.models import PerfilAcessoRH
from rh.models import Demissao
from rh.models import DependenteDeFuncionario
from rh.models import Feriado
from rh.models import Competencia
from rh.models import AtribuicaoDeCargo
from rh.models import GrupoDeCompetencia
from rh.models import CapacitacaoDeSubProcedimento
from rh.models import Procedimento
from rh.models import SubProcedimento
from rh.models import AtribuicaoDeResponsabilidade
from rh.models import AutorizacaoHoraExtra

from sorl.thumbnail.admin import AdminImageMixin

class ExperienciasProfissionaisFuncionarioInline(admin.StackedInline):
    model = ExperienciasProfissionaisFuncionario
    ordering = ['data_admissao',]
    extra = 0
    
class IdiomaFuncionarioInline(admin.StackedInline):
    ordering = ['nivel']
    model = IdiomaFuncionario
    extra = 0

class CursoFuncionarioInline(admin.StackedInline):
    ordering = ['data']
    model = CursoFuncionario
    extra = 0

class DependenteDeFuncionarioInline(admin.StackedInline):
    model = DependenteDeFuncionario
    extra = 0


class PeriodoTrabalhadoInline(admin.StackedInline):
    model = PeriodoTrabalhado
    extra = 0

class FuncionarioAdmin(AdminImageMixin, admin.ModelAdmin):
    search_fields = 'nome',
    save_on_top = True
    list_display = ('nome', 'email', 'cargo_atual', 'user', 'endereco_empresa_designado')
    list_display_links = list_display
    list_filter = ('cargo_atual',)
    filter_horizontal = 'competencias',
    inlines = [
        PeriodoTrabalhadoInline,
        IdiomaFuncionarioInline,
        CursoFuncionarioInline,
        ExperienciasProfissionaisFuncionarioInline,
        DependenteDeFuncionarioInline,
    ]

class SolicitacaoDeLicencaAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ['periodo_trabalhado__funcionario__nome',]
    list_filter = ('status', 'tipo', 'periodo_trabalhado__funcionario__cargo_atual__nome', 'inicio')
    list_display = ('periodo_trabalhado', 'data_criado', 'tipo', 'inicio', 'fim', 'status')
    list_display_links = list_display
    date_hierarchy = 'data_criado'

class PromocaoCargoAdmin(admin.ModelAdmin):
    save_on_top = True

class EntradaFolhaDePontoInline(admin.StackedInline):
    model = EntradaFolhaDePonto
    ordering = ['inicio']
    extra= 0

class FolhaDePontoAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('funcionario_mes_ano', 'periodo_trabalhado', 'autorizado', 'encerrado', 'funcionario_autorizador', 'total_horas')
    date_hierarchy = 'data_referencia'
    list_filter = 'data_referencia', 'periodo_trabalhado__funcionario', 'autorizado', 'encerrado',
    inlines = [EntradaFolhaDePontoInline]

class AtribuicaoDeCargoInline(admin.StackedInline):
    model = AtribuicaoDeCargo
    ordering = ['inicio']
    extra=0

class SolicitacaoDeLicencaInline(admin.StackedInline):
    model = SolicitacaoDeLicenca
    extra = 0

class PeriodoTrabalhadoAdmin(admin.ModelAdmin):
    list_filter = 'inicio', 'fim', 'funcionario', 'funcionario__cargo_atual'
    list_display = 'id', 'funcionario', 'inicio', 'fim'
    list_display_links = list_display
    inlines = [AtribuicaoDeCargoInline, SolicitacaoDeLicencaInline]

class FeriadoAdmin(admin.ModelAdmin):
    list_filter = 'importado_por_sync',
    list_display = 'data', 'nome', 'importado_por_sync'

class PerfilAcessoRHAdmin(admin.ModelAdmin):
    list_filter = 'user', 'analista', 'gerente',
    list_display = 'user',  'analista', 'gerente',

class EntradaFolhaDePontoAdmin(admin.ModelAdmin):
    list_filter = 'folha__periodo_trabalhado__funcionario', 'adicionado_por'
    list_display = 'folha', 'adicionado_por'
    list_display_links = list_display

class DemissaoAdmin(admin.ModelAdmin):
    list_filter = 'status', 'demitido', 'demissor'
    list_display = 'id', 'demitido', 'status', 'demissor'
    list_display_links = list_display

class RotinaExameMedicoAdmin(admin.ModelAdmin):
    list_filter = 'tipo', 'periodo_trabalhado__funcionario', 'realizado'
    list_display = 'id', 'tipo', 'periodo_trabalhado', 'realizado', 'data'
    date_hierarchy = 'data'
    filter_horizontal = 'exames',

class CompetenciaAdmin(admin.ModelAdmin):
    list_filter = 'grupo',

class CargoAdmin(admin.ModelAdmin):
    filter_horizontal = 'competencias', 'subprocedimentos', 'exame_medico_padrao'
    
class AtribuicaoDeCargoAdmin(admin.ModelAdmin):
    list_display = 'id', 'periodo_trabalhado', 'cargo', 'inicio', 'fim', 'local_empresa'
    list_display_links = list_display
    list_filter = 'periodo_trabalhado__funcionario',


def duplicate_event(modeladmin, request, queryset):
    for object in queryset:
        object.id = None
        object.save()
        
duplicate_event.short_description = "Duplicar Entrada Selecionada"

class PromocaoSalarioAdmin(admin.ModelAdmin):
    list_filter = 'periodo_trabalhado__funcionario',
    list_display = '__unicode__', 'data_promocao', 'valor_destino'
    #list_display_links = list_display
    actions = [duplicate_event]


class SubProcedimentoInline(admin.StackedInline):
    model = SubProcedimento
    extra = 0

class ProcedimentoAdmin(admin.ModelAdmin):
    inlines = [SubProcedimentoInline]

class SubProcedimentoAdmin(admin.ModelAdmin):
    list_filter = 'procedimento',

class AtribuicaoDeResponsabilidadeAdmin(admin.ModelAdmin):
    list_filter = 'tipo_de_treinamento',
    list_display = 'treinamento_realizado', 'tipo_de_treinamento', 'horas_treinadas', 'periodo_trabalhado'

class AutorizacaoHoraExtraAdmin(admin.ModelAdmin):
    list_display = 'periodo_trabalhado', 'quantidade', 'valor_total', 'data_execucao', 'solicitante', 'criado'


admin.site.register(Funcionario, FuncionarioAdmin)
admin.site.register(IdiomaFuncionario)
admin.site.register(ExperienciasProfissionaisFuncionario)
admin.site.register(Departamento)
admin.site.register(CursoFuncionario)
admin.site.register(PeriodoTrabalhado, PeriodoTrabalhadoAdmin)
admin.site.register(PromocaoSalario, PromocaoSalarioAdmin)
admin.site.register(PromocaoCargo, PromocaoCargoAdmin)
admin.site.register(SolicitacaoDeLicenca, SolicitacaoDeLicencaAdmin)
admin.site.register(FolhaDePonto, FolhaDePontoAdmin)
admin.site.register(PerfilAcessoRH, PerfilAcessoRHAdmin)
admin.site.register(TipoDeExameMedico)
admin.site.register(RotinaExameMedico, RotinaExameMedicoAdmin)
admin.site.register(Demissao, DemissaoAdmin)
admin.site.register(DependenteDeFuncionario)
admin.site.register(Feriado, FeriadoAdmin)
admin.site.register(EntradaFolhaDePonto, EntradaFolhaDePontoAdmin)
admin.site.register(GrupoDeCompetencia)
admin.site.register(Competencia, CompetenciaAdmin)
admin.site.register(Cargo, CargoAdmin)
admin.site.register(AtribuicaoDeCargo, AtribuicaoDeCargoAdmin)
admin.site.register(Procedimento, ProcedimentoAdmin)
admin.site.register(SubProcedimento, SubProcedimentoAdmin)
admin.site.register(CapacitacaoDeSubProcedimento)
admin.site.register(AtribuicaoDeResponsabilidade, AtribuicaoDeResponsabilidadeAdmin)
admin.site.register(AutorizacaoHoraExtra, AutorizacaoHoraExtraAdmin)