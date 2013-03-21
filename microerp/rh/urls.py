# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls do RH
urlpatterns = patterns('',
    url(r'^$', 'rh.views.home', name='home'),
    # funcionario
    url(r'^funcionarios$', 'rh.views.funcionarios', name='funcionarios'),
    url(r'^funcionarios/(?P<funcionario_id>[0-9]+)/$', 'rh.views.ver_funcionario', name='ver_funcionario'),
    url(r'^funcionarios/(?P<funcionario_id>[0-9]+)/demitir/$', 'rh.views.demitir_funcionario', name='demitir_funcionario'),
    # funcionario > folha de ponto
    url(r'^funcionarios/(?P<funcionario_id>[0-9]+)/folha_de_ponto/add/$', 'rh.views.folha_de_ponto_add', name='folha_de_ponto_add'),
    # funcionario > solicitacao licenca
    url(r'^funcionarios/(?P<funcionario_id>[0-9]+)/licenca/add/$', 'rh.views.solicitacao_licenca_add', name='solicitacao_licenca_add'),
    
    # exames medicos
    url(r'^exames_medicos/$', 'rh.views.exames_medicos', name='exames_medicos'),
    url(r'^exames_medicos/(?P<exame_id>[0-9]+)/realizado_hoje/$', 'rh.views.exames_medicos_exame_realizado_hoje', name='exame_realizado_hoje'),
    url(r'^exames_medicos/(?P<exame_id>[0-9]+)/$', 'rh.views.exames_medicos_ver', name='exames_medicos_ver'),

    # solicitações de licença
    url(r'^solicitacao_licencas/$', 'rh.views.solicitacao_licencas', name='solicitacao_licencas'),
    url(r'^solicitacao_licencas/(?P<solicitacao_id>[0-9]+)/autorizar/$', 'rh.views.solicitacao_licencas_autorizar', name='solicitacao_licencas_autorizar'),
    
    # demissoes
    url(r'^processos_demissao/$', 'rh.views.processos_demissao', name='processos_demissao'),
    
)
