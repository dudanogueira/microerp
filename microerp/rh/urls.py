# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from rh import views

# urls do RH
urlpatterns = [
    url(r'^$', views.home, name='home'),
    # funcionario
    url(r'^funcionarios/$', views.funcionarios, name='funcionarios'),
    url(r'^funcionario/(?P<funcionario_id>[0-9]+)/$', views.ver_funcionario, name='ver_funcionario'),
    url(r'^funcionario/(?P<funcionario_id>[0-9]+)/demitir/$', views.demitir_funcionario, name='demitir_funcionario'),
    url(r'^funcionario/(?P<funcionario_id>[0-9]+)/promover/$', views.promover_funcionario, name='promover_funcionario'),
    # funcionario > solicitacao licenca
    url(r'^funcionario/(?P<funcionario_id>[0-9]+)/licenca/add/$', views.solicitacao_licenca_add, name='solicitacao_licenca_add'),
    # funcionario > relatorios > banco de horas
    url(r'^funcionario/(?P<funcionario_id>[0-9]+)/controle/banco_de_hora/$', views.controle_banco_de_horas_do_funcionario, name='controle_banco_de_horas_do_funcionario'),
    url(r'^funcionario/(?P<funcionario_id>[0-9]+)/controle/banco_de_hora/folha/(?P<folha_id>[0-9]+)/$', views.controle_banco_de_horas_do_funcionario_gerenciar, name='controle_banco_de_horas_do_funcionario_gerenciar'),
    # funcionario > hora extra
    url(r'^funcionario/(?P<funcionario_id>[0-9]+)/hora-extra/$', views.adicionar_hora_extra, name='adicionar_hora_extra'),
    url(r'^funcionario/(?P<funcionario_id>[0-9]+)/hora-extra/(?P<autorizacao_hora_extra_id>[0-9]+)/imprimir$', views.imprimir_hora_extra, name='imprimir_hora_extra'),
    # funcionarios > relatorios
    url(r'^funcionarios/relatorios/ativos/$', views.funcionarios_relatorios_listar_ativos, name='funcionarios_listar_ativos'),

    # funcionarios > relatorios > aniversários
    url(r'^funcionarios/relatorios/ativos/aniversarios$', views.funcionarios_relatorios_listar_ativos_aniversarios, name='funcionarios_relatorios_listar_ativos_aniversarios'),
    url(r'^competencias/matriz/$', views.matriz_de_competencias, name='matriz_de_competencias'),

    # exames medicos
    url(r'^exames-medicos/$', views.exames_medicos, name='exames_medicos'),
    url(r'^exames-medicos/relatorios/custos/$', views.exames_medicos_relatorios_custos, name='exames_medicos_relatorios_custos'),
    url(r'^exames-medicos/(?P<exame_id>[0-9]+)/realizado_hoje/$', views.exames_medicos_exame_realizado_hoje, name='exame_realizado_hoje'),
    url(r'^exames-medicos/(?P<exame_id>[0-9]+)/$', views.exames_medicos_ver, name='exames_medicos_ver'),

    # solicitações de licença
    url(r'^solicitacao-licencas/$', views.solicitacao_licencas, name='solicitacao_licencas'),
    url(r'^solicitacao-licencas/(?P<solicitacao_id>[0-9]+)/autorizar/$', views.solicitacao_licencas_autorizar, name='solicitacao_licencas_autorizar'),

    # CONTROLES
    url(r'^controle/ferias/$', views.controle_de_ferias, name='controle_de_ferias'),

    # controle de banco de horas
    url(r'^controle/banco-de-horas/$', views.controle_de_banco_de_horas, name='controle_de_banco_de_horas'),

    # demissoes
    url(r'^processos-demissao/$', views.processos_demissao, name='processos_demissao'),
    url(r'^processos-demissao/finalizar/(?P<processo_id>[0-9]+)/$', views.processos_demissao_finalizar, name='processo_demissao_finalizar'),

    # demissoes
    url(r'^processos-admissao/$', views.processos_admissao, name='processos_admissao'),
    url(r'^processos-admissao/admitir/$', views.processos_admissao_admitir, name='processos_admissao_admitir'),

    # promocoes
    url(r'^promocoes/$', views.processos_promocao, name='processos_promocao'),

    # Capacitacao
    url(r'^capacitacoes/$',  views.capacitacao_de_procedimentos, name='capacitacao_de_procedimentos'),
    url(r'^capacitacoes/funcionario/(?P<funcionario_id>[0-9]+)/gerar-ar/$', views.capacitacao_de_procedimentos_gerar_ar, name='capacitacao_de_procedimentos_gerar_ar'),
    url(r'^capacitacoes/funcionario/(?P<funcionario_id>[0-9]+)/ver/$', views.capacitacao_de_procedimentos_ver_ar, name='capacitacao_de_procedimentos_ver_ar'),
    url(r'^capacitacoes/funcionario/(?P<funcionario_id>[0-9]+)/confirmar/(?P<atribuicao_responsabilidade_id>[0-9]+)/$', views.capacitacao_de_procedimentos_confirmar, name='capacitacao_de_procedimentos_confirmar'),
    url(r'^capacitacoes/funcionario/(?P<funcionario_id>[0-9]+)/remover/(?P<atribuicao_responsabilidade_id>[0-9]+)$', views.capacitacao_de_procedimentos_remover_ar, name='capacitacao_de_procedimentos_remover_ar'),

    # controle de epi
    url(r'^controle-de-epi/$', views.controle_de_epi, name='controle_de_epi'),
    url(r'^controle-de-epi/adicionar/$', views.controle_de_epi_adicionar, name='controle_de_epi_adicionar'),
    url(r'^controle-de-epi/(?P<controle_id>[0-9]+)/imprimir/$', views.controle_de_epi_imprimir, name='controle_de_epi_imprimir'),
    url(r'^controle-de-epi/(?P<controle_id>[0-9]+)/vincular-arquivo/$', views.controle_de_epi_vincular_arquivo, name='controle_de_epi_vincular_arquivo'),
    url(r'^controle-de-epi/(?P<controle_id>[0-9]+)/(?P<linha_id>[0-9]+)/retornar-epi/$', views.controle_de_epi_retornar, name='controle_de_epi_retornar'),
    # controle de ferramentas
    url(r'^controle-de-ferramenta/$', views.controle_de_ferramenta, name='controle_de_ferramenta'),
    url(r'^controle-de-ferramenta/adicionar/$', views.controle_de_ferramenta_adicionar, name='controle_de_ferramenta_adicionar'),
    url(r'^controle-de-ferramenta/(?P<controle_id>[0-9]+)/imprimir/$', views.controle_de_ferramenta_imprimir, name='controle_de_ferramenta_imprimir'),
    url(r'^controle-de-ferramenta/(?P<controle_id>[0-9]+)/vincular-arquivo/$', views.controle_de_ferramenta_vincular_arquivo, name='controle_de_ferramenta_vincular_arquivo'),
    url(r'^controle-de-ferramenta/(?P<controle_id>[0-9]+)/(?P<linha_id>[0-9]+)/retornar-ferramenta/$', views.controle_de_ferramenta_retornar, name='controle_de_ferramenta_retornar'),
    # indicadores
    url(r'^indicadores/$', views.indicadores_do_rh, name='indicadores_do_rh'),
]
