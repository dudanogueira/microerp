# -*- coding: utf-8 -*-
from django.contrib import admin

from models import Solicitacao, TipoSolicitacao, PerfilAcessoSolicitacao

class SolicitacaoAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = 'id', 'procede', 'status', 'responsavel_correcao', 'responsavel_contato', 'responsavel_visto'
    list_filter = 'status', 'responsavel_correcao', 'responsavel_contato', 'responsavel_visto'
    fieldsets = (
        ('Contato', {
            'fields': ('cliente', 'precliente', 'contato')
        }),
        ('Solicitação', {
            'fields': ('prioridade', 'descricao', 'tipo', 'status', 'procede', 'nao_procede_porque', )
        }),
        ('Resolução', {
            'fields': ('providencia', 'despachado_data', 'resolucao_final', 'resolucao_final_data')
        }),
        ('Abrangência', {
            'fields': ('departamentos_afetados', 'departamento_direto',)
        }),
        ('Responsáveis', {
            'classes': ('collapse',),
            'fields': ('responsavel_correcao', 'correcao_iniciada', 'responsavel_contato', 'contato_realizado', 'responsavel_visto')
        }),
    )
    filter_horizontal = 'departamentos_afetados',

admin.site.register(Solicitacao, SolicitacaoAdmin)
admin.site.register(TipoSolicitacao)
admin.site.register(PerfilAcessoSolicitacao)