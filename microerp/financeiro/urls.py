# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# urls do Cadastro
urlpatterns = patterns('',
    url(r'^$', 'financeiro.views.home', name='home'),
    # Contratos
    url(r'^contratos-a-lancar$', 'financeiro.views.contratos_a_lancar', name='contratos_a_lancar'),
    url(r'^contrato/(?P<contrato_id>[0-9]+)/ver$', 'financeiro.views.ver_contrato', name='ver_contrato'),
    url(r'^contrato/(?P<contrato_id>[0-9]+)/realizar-lancamento$', 'financeiro.views.realizar_lancamento', name='realizar_lancamento'),
    url(r'^contrato/(?P<contrato_id>[0-9]+)/adicionar-lancamento$', 'financeiro.views.contrato_adicionar_lancamento', name='contrato_adicionar_lancamento'),
    url(r'^contrato/(?P<contrato_id>[0-9]+)/fechar-contrato$', 'financeiro.views.contrato_fechar', name='contrato_fechar'),
    # lancamentos
    url(r'^lancamentos/a-receber$', 'financeiro.views.lancamentos_a_receber', name='lancamentos_a_receber'),
)
