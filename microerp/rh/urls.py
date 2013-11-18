# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls do RH
urlpatterns = patterns('',
    url(r'^$', 'rh.views.home', name='home'),
    # funcionario
    url(r'^funcionarios/$', 'rh.views.funcionarios', name='funcionarios'),
    url(r'^funcionario/(?P<funcionario_id>[0-9]+)/$', 'rh.views.ver_funcionario', name='ver_funcionario'),
    url(r'^funcionario/(?P<funcionario_id>[0-9]+)/demitir/$', 'rh.views.demitir_funcionario', name='demitir_funcionario'),
    url(r'^funcionario/(?P<funcionario_id>[0-9]+)/promover/$', 'rh.views.promover_funcionario', name='promover_funcionario'),
    # funcionario > solicitacao licenca
    url(r'^funcionario/(?P<funcionario_id>[0-9]+)/licenca/add/$', 'rh.views.solicitacao_licenca_add', name='solicitacao_licenca_add'),
    # funcionario > relatorios > banco de horas
    url(r'^funcionario/(?P<funcionario_id>[0-9]+)/controle/banco_de_hora/$', 'rh.views.controle_banco_de_horas_do_funcionario', name='controle_banco_de_horas_do_funcionario'),
    url(r'^funcionario/(?P<funcionario_id>[0-9]+)/controle/banco_de_hora/folha/(?P<folha_id>[0-9]+)/$', 'rh.views.controle_banco_de_horas_do_funcionario_gerenciar', name='controle_banco_de_horas_do_funcionario_gerenciar'),
    
    # funcionarios > relatorios
    url(r'^funcionarios/relatorios/ativos/$', 'rh.views.funcionarios_relatorios_listar_ativos', name='funcionarios_listar_ativos'),

    # funcionarios > relatorios > aniversários
    url(r'^funcionarios/relatorios/ativos/aniversarios$', 'rh.views.funcionarios_relatorios_listar_ativos_aniversarios', name='funcionarios_relatorios_listar_ativos_aniversarios'),    
    url(r'^competencias/matriz/$', 'rh.views.matriz_de_competencias', name='matriz_de_competencias'),
    
    # exames medicos
    url(r'^exames-medicos/$', 'rh.views.exames_medicos', name='exames_medicos'),
    url(r'^exames-medicos/(?P<exame_id>[0-9]+)/realizado_hoje/$', 'rh.views.exames_medicos_exame_realizado_hoje', name='exame_realizado_hoje'),
    url(r'^exames-medicos/(?P<exame_id>[0-9]+)/$', 'rh.views.exames_medicos_ver', name='exames_medicos_ver'),

    # solicitações de licença
    url(r'^solicitacao-licencas/$', 'rh.views.solicitacao_licencas', name='solicitacao_licencas'),
    url(r'^solicitacao-licencas/(?P<solicitacao_id>[0-9]+)/autorizar/$', 'rh.views.solicitacao_licencas_autorizar', name='solicitacao_licencas_autorizar'),

    # CONTROLES
    url(r'^controle/ferias/$', 'rh.views.controle_de_ferias', name='controle_de_ferias'),    

    # controle de banco de horas
    url(r'^controle/banco-de-horas/$', 'rh.views.controle_de_banco_de_horas', name='controle_de_banco_de_horas'),    
    
    # demissoes
    url(r'^processos-demissao/$', 'rh.views.processos_demissao', name='processos_demissao'),
    
    # promocoes
    url(r'^promocoes/$', 'rh.views.processos_promocao', name='processos_promocao'),
    # controle de epi
    url(r'^controle-de-epi/$', 'rh.views.controle_de_epi', name='controle_de_epi'),
    url(r'^controle-de-epi/adicionar/$', 'rh.views.controle_de_epi_adicionar', name='controle_de_epi_adicionar'),
    url(r'^controle-de-epi/(?P<controle_id>[0-9]+)/imprimir/$', 'rh.views.controle_de_epi_imprimir', name='controle_de_epi_imprimir'),
    url(r'^controle-de-epi/(?P<controle_id>[0-9]+)/vincular-arquivo/$', 'rh.views.controle_de_epi_vincular_arquivo', name='controle_de_epi_vincular_arquivo'),
    url(r'^controle-de-epi/(?P<controle_id>[0-9]+)/(?P<linha_id>[0-9]+)/retornar-epi/$', 'rh.views.controle_de_epi_retornar', name='controle_de_epi_retornar'),
    # controle de ferramentas
    url(r'^controle-de-ferramenta/$', 'rh.views.controle_de_ferramenta', name='controle_de_ferramenta'),
    url(r'^controle-de-ferramenta/adicionar/$', 'rh.views.controle_de_ferramenta_adicionar', name='controle_de_ferramenta_adicionar'),
    url(r'^controle-de-ferramenta/(?P<controle_id>[0-9]+)/imprimir/$', 'rh.views.controle_de_ferramenta_imprimir', name='controle_de_ferramenta_imprimir'),
    url(r'^controle-de-ferramenta/(?P<controle_id>[0-9]+)/vincular-arquivo/$', 'rh.views.controle_de_ferramenta_vincular_arquivo', name='controle_de_ferramenta_vincular_arquivo'),
    url(r'^controle-de-ferramenta/(?P<controle_id>[0-9]+)/(?P<linha_id>[0-9]+)/retornar-ferramenta/$', 'rh.views.controle_de_ferramenta_retornar', name='controle_de_ferramenta_retornar'),
    # indicadores
    url(r'^indicadores/$', 'rh.views.indicadores_do_rh', name='indicadores_do_rh'),
)
