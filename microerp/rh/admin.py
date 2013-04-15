# -*- coding: utf-8 -*-
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


from sorl.thumbnail.admin import AdminImageMixin

class ExperienciasProfissionaisFuncionarioInline(admin.StackedInline):
    model = ExperienciasProfissionaisFuncionario
    ordering = ['data_admissao']
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

class FuncionarioAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('nome', 'email', 'cargo_atual')
    list_display_links = list_display
    list_filter = ('cargo_atual',)
    inlines = [
        IdiomaFuncionarioInline,
        CursoFuncionarioInline,
        ExperienciasProfissionaisFuncionarioInline,
        DependenteDeFuncionarioInline,
    ]


class SolicitacaoDeLicencaAdmin(admin.ModelAdmin):
    search_fields = ['funcionario__nome',]
    list_filter = ('status', 'tipo', 'funcionario__cargo_atual__nome', 'inicio')
    list_display = ('funcionario', 'data_criado', 'tipo', 'inicio', 'fim', 'status')
    list_display_links = list_display
    date_hierarchy = 'data_criado'

class PromocaoCargoAdmin(admin.ModelAdmin):
    list_display = ('beneficiario', 'data_solicitacao', 'cargo_antigo', 'cargo_novo', 'aprovado', 'avaliado', 'criado')


class EntradaFolhaDePontoInline(admin.StackedInline):
    model = EntradaFolhaDePonto
    ordering = ['hora']
    extra= 0

class FolhaDePontoAdmin(admin.ModelAdmin):
    list_display = ('funcionario_mes_ano', 'funcionario', 'autorizado', 'encerrado', 'funcionario_autorizador')
    date_hierarchy = 'data_referencia'
    list_filter = 'data_referencia', 'funcionario', 'autorizado', 'encerrado',
    inlines = [EntradaFolhaDePontoInline]

class PeriodoTrabalhadoAdmin(admin.ModelAdmin):
    list_filter = 'inicio', 'fim', 'funcionario'

class FeriadoAdmin(admin.ModelAdmin):
    list_filter = 'importado_por_sync',
    list_display = 'data', 'nome', 'importado_por_sync'

class PerfilAcessoRHAdmin(admin.ModelAdmin):
    list_filter = 'user', 'analista', 'gerente',
    list_display = 'user',  'analista', 'gerente',

admin.site.register(Funcionario, FuncionarioAdmin)
admin.site.register(IdiomaFuncionario)
admin.site.register(ExperienciasProfissionaisFuncionario)
admin.site.register(Cargo)
admin.site.register(Departamento)
admin.site.register(CursoFuncionario)
admin.site.register(PeriodoTrabalhado, PeriodoTrabalhadoAdmin)
admin.site.register(PromocaoSalario)
admin.site.register(PromocaoCargo, PromocaoCargoAdmin)
admin.site.register(SolicitacaoDeLicenca, SolicitacaoDeLicencaAdmin)
admin.site.register(FolhaDePonto, FolhaDePontoAdmin)
admin.site.register(PerfilAcessoRH, PerfilAcessoRHAdmin)
admin.site.register(TipoDeExameMedico)
admin.site.register(RotinaExameMedico)
admin.site.register(Demissao)
admin.site.register(DependenteDeFuncionario)
admin.site.register(Feriado, FeriadoAdmin)